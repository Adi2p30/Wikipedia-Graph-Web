import wikipediaapi
import threading
import queue
import random
import time
import os
import json
import webbrowser
import logging
from collections import Counter

import networkx as nx                # still useful for any future analytics
import matplotlib.pyplot as plt      # idem
from pyvis.network import Network

# ────────────────────────────────  basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ────────────────────────────────  MAIN CLASS
class WikipediaNetworkExplorer:
    def __init__(
        self,
        language="en",
        user_agent=(
            "WikipediaNetworkExplorer/1.0 "
            "(https://example.com/bot; myemail@example.com)"
        ),
    ):
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent=user_agent,
        )
        self.cache_dir = "wiki_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.reset()

    # ───────── state helpers
    def reset(self):
        self.all_paths_explored = []
        self.queue1, self.queue2 = queue.Queue(), queue.Queue()
        self.visited1, self.visited2 = {}, {}
        self.lock1, self.lock2 = threading.Lock(), threading.Lock()
        self.connection_found = threading.Event()
        self.final_path, self.meeting_node = [], None
        self.page_data_cache, self.visit_count = {}, Counter()
        self.edges_data = {}
        logging.info("Explorer reset.")

    # ───────── caching layer
    def _get_page_data(self, title: str):
        if title in self.page_data_cache:
            return self.page_data_cache[title]

        safe = "".join(c if c.isalnum() or c in (" ", "-") else "_" for c in title)
        cache_file = os.path.join(self.cache_dir, f"{safe}.json")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.page_data_cache[title] = data
                return data
            except (OSError, json.JSONDecodeError):
                logging.warning("Corrupt cache for %s – refetching.", title)

        page = self.wiki.page(title)
        if not page.exists():
            data = {"summary": "Page not found", "categories": []}
        else:
            summary = page.summary
            data = {
                "summary": summary[:200] + "…" if len(summary) > 200 else summary,
                "categories": list(page.categories.keys()),
            }

        # write-through
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except OSError as e:
            logging.error("Could not write cache file: %s", e)

        self.page_data_cache[title] = data
        return data

    # ───────── link scraping
    def _get_links(self, page, max_links=500, filter_words=None):
        try:
            links = list(page.links.keys())
            if filter_words:
                lower = [w.lower() for w in filter_words]
                links = [
                    L for L in links
                    if not any(w in L.lower() for w in lower)
                ]
            return links[:max_links]
        except Exception as e:
            logging.error("Link scrape failed for %s: %s", page.title, e)
            return []

    # ───────── tiny heuristic classifier
    def _categorize_node(self, title: str) -> str:
        if title in self.page_data_cache and "node_type" in self.page_data_cache[title]:
            return self.page_data_cache[title]["node_type"]

        categories = [
            c.lower() for c in self._get_page_data(title).get("categories", [])
        ]

        kw = {
            "person": [
                "births", "people", "biography", "actor", "musician",
                "writer", "scientist", "politician",
            ],
            "place": [
                "countries", "cities", "states", "regions",
                "locations", "geography", "settlements",
            ],
            "organization": ["companies", "organizations", "institutions",
                             "universities", "governments"],
            "event": ["events", "conflicts", "wars", "battles",
                      "festivals", "elections"],
            "work": ["films", "books", "albums", "songs",
                     "paintings", "software", "video games"],
            "concept": ["concepts", "theories", "philosophies",
                        "ideas", "movements"],
            "science": ["science", "technology", "biology", "chemistry",
                        "physics", "mathematics", "computing"],
            "history": ["history", "historical", "ancient", "medieval", "century"],
            "list": ["lists of", "list of"],
        }

        node_type = "list" if "list of" in title.lower() else "other"
        if node_type == "other":                                # FIX
            for cat_type, kws in kw.items():                    # FIX
                if any(kwd in cat for cat in categories         # FIX
                                      for kwd in kws):          # FIX
                    node_type = cat_type                        # FIX
                    break

        # cache result
        self.page_data_cache.setdefault(title, {})["node_type"] = node_type
        return node_type

    # ───────── reconstruction util
    def _reconstruct_path(self, end, visited):
        path, cur = [], end
        while cur is not None:
            path.append(cur)
            cur = visited.get(cur, {}).get("parent")
        return list(reversed(path))

    # ───────── BFS worker
    def _bfs_step(
        self, q, visited_self, visited_other,
        lock_self, lock_other,
        forward, max_links, filter_words
    ):
        if self.connection_found.is_set() or q.empty():
            return
        try:
            path = q.get_nowait()
            node = path[-1]
            depth = visited_self[node]["depth"]

            self.visit_count[node] += 1
            page = self.wiki.page(node)
            if not page.exists():
                q.task_done()
                return

            from_type = self._categorize_node(node)
            links = self._get_links(page, max_links, filter_words)
            random.shuffle(links)

            for link in links:
                if self.connection_found.is_set():
                    break
                with lock_other:
                    if link in visited_other:
                        self.meeting_node = link
                        p1 = self._reconstruct_path(node if forward else link,
                                                    self.visited1)
                        p2 = self._reconstruct_path(link if forward else node,
                                                    self.visited2)
                        self.final_path = p1 + list(reversed(p2[1:]))
                        self.connection_found.set()
                        return

                with lock_self:
                    if link not in visited_self:
                        visited_self[link] = {"depth": depth + 1, "parent": node}
                        q.put(path + [link])
                        self.all_paths_explored.append(path + [link])
                        # edge meta (direction-agnostic key)
                        ekey = tuple(sorted((node, link)))      # FIX
                        if ekey not in self.edges_data:
                            self.edges_data[ekey] = {
                                "from_type": from_type,
                                "to_type": self._categorize_node(link),
                            }
            q.task_done()
        except queue.Empty:
            pass
        except Exception:
            logging.exception("Error during BFS step")

    def _worker(self, *args):
        while not self.connection_found.is_set():
            self._bfs_step(*args)
            time.sleep(0.01)

    # ───────── VISUALISATION (unchanged aside from color-border fix)
    def visualize_with_pyvis(
        self, source, destination, final_path,
        nodes_context, edges_context,
        filename="wiki_graph.html"
    ):
        net = Network(
            bgcolor="#222", font_color="white",
            height="800px", width="100%", directed=True,
            notebook=False, cdn_resources="remote"
        )

        category_colors = {
            "person": "#FF6347", "place": "#90EE90",
            "organization": "#87CEEB", "event": "#FFD700",
            "work": "#DA70D6", "concept": "#AFEEEE",
            "science": "#6495ED", "history": "#F4A460",
            "list": "#D3D3D3", "other": "#B0C4DE",
        }
        default_color = category_colors["other"]

        nodes_to_add = set(final_path)
        for u, v in edges_context:
            if u in final_path:
                nodes_to_add.add(v)
            if v in final_path:
                nodes_to_add.add(u)

        for n in nodes_to_add:
            data = self._get_page_data(n)
            kind = self._categorize_node(n)
            visits = self.visit_count.get(n, 1)

            node_style = {
                "label": n,
                "title": (
                    f"<b>{n}</b><br>"
                    f"Category: {kind}<br>"
                    f"Visits: {visits}<br>"
                    f"{data['summary']}"
                ),
                "color": category_colors.get(kind, default_color),
                "size": 10 + min(20, 0.5 * visits),
            }
            if n in (source, destination):
                node_style["color"] = {"border": "#FFFFFF",
                                       "background": node_style["color"]}
                node_style["borderWidth"] = 4                # FIX border handling
            elif n in final_path:
                node_style["color"] = {"border": "#FFFF00",
                                       "background": node_style["color"]}
                node_style["borderWidth"] = 2                # FIX

            net.add_node(n, **node_style)

        added = set()
        for u, v in edges_context:
            if u in nodes_to_add and v in nodes_to_add:
                key = tuple(sorted((u, v)))
                if key in added:
                    continue
                added.add(key)
                color = "#00FFFF" if {u, v} <= set(final_path) else \
                        category_colors.get(
                            self.edges_data.get(key, {}).get("from_type", "other"),
                            default_color,
                        )
                net.add_edge(u, v, color=color, width=4 if color == "#00FFFF" else 1)

        net.set_options("""var options = { "physics": { "barnesHut": { "gravitationalConstant": -8000 } } }""")
        net.save_graph(filename)
        logging.info("Visualisation saved → %s", filename)
        return os.path.abspath(filename)

    # ───────── public API
    def find_connection(
        self, source, destination,
        max_links_per_page=500,
        num_threads=10,
        filter_words=None,
        visualize=True,
        filename="wiki_graph.html",
        auto_open=True,
    ):
        self.reset()
        t0 = time.time()

        if filter_words is None:
            filter_words = [
                "wikipedia:", "wikimedia:", "category:", "template:",
                "help:", "portal:", "file:", "special:", "user:", "talk:"
            ]

        sp, dp = self.wiki.page(source), self.wiki.page(destination)
        if not sp.exists() or not dp.exists():
            print("Source or destination page missing.")
            return None
        if source == destination:
            return {"found": True, "degrees": 0, "path": [source]}

        self.queue1.put([source])
        self.visited1[source] = {"depth": 0, "parent": None}
        self.queue2.put([destination])
        self.visited2[destination] = {"depth": 0, "parent": None}

        threads = []
        for _ in range(max(1, num_threads // 2)):
            threads += [
                threading.Thread(target=self._worker,
                                 args=(self.queue1, self.visited1, self.visited2,
                                       self.lock1, self.lock2, True,
                                       max_links_per_page, filter_words),
                                 daemon=True),
                threading.Thread(target=self._worker,
                                 args=(self.queue2, self.visited2, self.visited1,
                                       self.lock2, self.lock1, False,
                                       max_links_per_page, filter_words),
                                 daemon=True),
            ]
        for t in threads:
            t.start()

        while not self.connection_found.is_set():
            if self.queue1.empty() and self.queue2.empty():
                break
            time.sleep(0.1)

        self.connection_found.set()
        for t in threads:
            t.join(timeout=2)

        Δt = time.time() - t0
        explored = len(self.visited1) + len(self.visited2)

        if self.final_path:
            result = {
                "found": True,
                "degrees": len(self.final_path) - 1,
                "path": self.final_path,
                "time": Δt,
                "nodes_explored": explored,
                "visualization": None,
            }
            if visualize:
                nodes_ctx = set(self.visited1) | set(self.visited2)
                edges_ctx = {
                    tuple(sorted((p[i], p[i + 1])))
                    for p in self.all_paths_explored
                    for i in range(len(p) - 1)
                }
                viz = self.visualize_with_pyvis(
                    source, destination, self.final_path,
                    nodes_ctx, edges_ctx, filename
                )
                result["visualization"] = viz
                if auto_open:
                    webbrowser.open(f"file://{viz}")
            return result
        else:
            return {"found": False, "time": Δt, "nodes_explored": explored}

# ────────────────────────────────  small demo
if __name__ == "__main__":
    explorer = WikipediaNetworkExplorer()
    res = explorer.find_connection(
        "Six degrees of separation", "Kevin Bacon",
        max_links_per_page=300, num_threads=20,
        visualize=False
    )
    print(res)
