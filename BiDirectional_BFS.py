import wikipediaapi
import threading
import queue
import networkx as nx
import matplotlib.pyplot as plt

wiki_wiki = wikipediaapi.Wikipedia(
    language="en",
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent="Aditya Pachpande",
)


queue1 = queue.Queue()
queue2 = queue.Queue()


past1 = {}
past2 = {}


lock1 = threading.Lock()
lock2 = threading.Lock()


connection_found = threading.Event()


def get_links(page, max_links=800):
    links = page.links
    return [link for link in links.keys()][:max_links]


def BFS_root(result, max_links):
    while not queue1.empty() and not connection_found.is_set():
        path = queue1.get()
        page_title = path[-1]
        current_page = wiki_wiki.page(page_title)

        if current_page.exists():
            links = get_links(current_page, max_links)
            for link in links:
                if "thing" in link:
                    continue
                with lock2:
                    if link in past2:
                        result["found"] = True
                        result["degrees"] = past1[page_title] + past2[link] - 2
                        result["path"] = path + [link]
                        connection_found.set()
                        return
                with lock1:
                    if link not in past1:
                        past1[link] = past1[page_title] + 1
                        new_path = list(path)
                        new_path.append(link)
                        queue1.put(new_path)
                print(link)
        queue1.task_done()


def BFS_dest(result, max_links):
    while not queue2.empty() and not connection_found.is_set():
        path = queue2.get()
        page_title = path[-1]
        current_page = wiki_wiki.page(page_title)

        if current_page.exists():
            links = get_links(current_page, max_links)
            for link in links:
                if "thing" in link:
                    continue
                with lock1:
                    if link in past1 and "identifier" not in link:
                        result["found"] = True
                        result["degrees"] = past1[link] + past2[page_title] - 2
                        result["path"] = [link] + path
                        connection_found.set()
                        return
                with lock2:
                    if link not in past2 and "identifier" not in link:
                        past2[link] = past2[page_title] + 1
                        new_path = list(path)
                        new_path.append(link)
                        queue2.put(new_path)
                print(link)

        queue2.task_done()


def visualize_wikipedia_path(path):
    if len(path) < 1:
        print("Path is too short to visualize.")
        return

    G = nx.DiGraph()

    for i in range(len(path) - 1):
        G.add_edge(path[i], path[i + 1])

    pos = nx.spring_layout(G, k=0.5, iterations=50)

    plt.figure(figsize=(10, 7))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="skyblue",
        node_size=2000,
        edge_color="gray",
        font_size=10,
        font_weight="bold",
        arrows=True,
    )

    plt.title(f"Path from '{path[0]}' to '{path[-1]}'", fontsize=15)
    plt.show()


def find_degrees_of_relation_bidirectional(
    thing1, thing2, max_links=5000, num_threads=80
):
    page1 = wiki_wiki.page(thing1)
    page2 = wiki_wiki.page(thing2)

    if not page1.exists() or not page2.exists():
        print(f"One of the pages does not exist: {thing1}, {thing2}")
        return -1, []

    queue1.put([thing1])
    past1[thing1] = 1
    queue2.put([thing2])
    past2[thing2] = 1

    result = {"found": False, "degrees": -1, "path": []}

    threads = []
    for _ in range(num_threads // 2):
        thread = threading.Thread(target=BFS_root, args=(result, max_links))
        threads.append(thread)
        thread.start()

    for _ in range(num_threads // 2):
        thread = threading.Thread(target=BFS_dest, args=(result, max_links))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return (result["degrees"], result["path"]) if result["found"] else (-1, [])


thing1 = "Mac Pro"
thing2 = "Puff pastry"
degrees, path = find_degrees_of_relation_bidirectional(
    thing1, thing2, max_links=2000, num_threads=40
)

if degrees != -1:
    path.append(thing2)
    print(
        f"The degrees of relation between '{thing1}' and '{thing2}' is {degrees}. Path: {path}"
    )
    visualize_wikipedia_path(path)
else:
    print(f"No relation found between '{thing1}' and '{thing2}'.")
