import wikipediaapi
from urllib.parse import urlparse
import json

wikiwiki = wikipediaapi.Wikipedia(
    user_agent='Aditya Pachpande',
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)


def getlinks(page):
    links = page.links
    return [link for link in links.keys()]


def urltotitle(url):
    title = url.split('/')[-1]
    return title


def fetch_recursive(starttext, depth):
    linkdict = {}
    visitedlinks = set()

    def recursive_traverse(text, currentdepth):
        if currentdepth == depth:
            return
        page = wikiwiki.page(text)

        links = getlinks(page)
        linkdict[text] = links
        if page.exists():
            for link in links:
                if link not in visitedlinks:
                    visitedlinks.add(link)
                    recursive_traverse(link, currentdepth + 1)

    recursive_traverse(starttext, 0)
    return linkdict


starttext = "Cristiano Ronaldo"
depth = 2
finaldict = fetch_recursive(starttext, depth)

with open(starttext+ str(depth) +'_output.json', 'w') as json_file:
    json.dump(finaldict, json_file, indent=4)

print("Data saved")
