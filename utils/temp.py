import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent="MyProjectName (merlin@example.com)",
    language="en",
    extract_format=wikipediaapi.ExtractFormat.WIKI,
)
page = wiki_wiki.page("Cristiano Ronaldo")

links = page.links

print(links)
