import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='MyProjectName (merlin@example.com)',
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)


def get_links(page):
    links = page.links
    return [link for link in links.keys()]


def find_degrees_of_relation(thing1, thing2):
    visited = set()
    queue = [[thing1]]

    while queue:
        path = queue.pop(0)
        page = wiki_wiki.page(path[-1])

        if page.exists():
            links = get_links(page)

            for link in links:
                if link == thing2:
                    return len(path)

                if link not in visited:
                    visited.add(link)
                    new_path = list(path)
                    new_path.append(link)
                    queue.append(new_path)

    return -1


thing1 = "Ananya Panday"
thing2 = "Grand Theft Auto VI"
degrees = find_degrees_of_relation(thing1, thing2)
if degrees != -1:
    print(f"The degrees of relation between '{thing1}' and '{thing2}' is {degrees}.")
else:
    print(f"No relation found between '{thing1}' and '{thing2}'.")
