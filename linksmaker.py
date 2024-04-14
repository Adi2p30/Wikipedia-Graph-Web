import wikipediaapi
from urllib.parse import urlparse

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='MyProjectName (merlin@example.com)',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI
)
page_py = wiki_wiki.page('Python_(programming_language)')

def getlinks(page):
    links = page.links
    for title in sorted(links.keys()):
        print("%s: %s" % (title, links[title]))

def urltopagetitle(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    title = path.split('/')[-1]
    return title

def iteration(prevresult)
    for i in prevresult:
        temp[starttext][i] = urltopagetitle(getlinks(i))



linkdict = {}

starttext = "Cristiano Ronaldo"
temp = {starttext:[]}

firstresult = urltopagetitle(getlinks(starttext))

path =
for i in range(0,4):
    for j in temp.keys():

        if page.exists():
            for j in
        else:
            pass
    temp =

