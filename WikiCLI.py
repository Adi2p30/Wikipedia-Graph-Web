import click
import wikipediaapi
from BiDirectional_BFS import find_degrees_of_relation_bidirectional

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent="MyProjectName (merlin@example.com)",
    language="en",
    extract_format=wikipediaapi.ExtractFormat.WIKI,
)


def fetch_summary(page_title):

    page = wiki_wiki.page(page_title)
    return page.summary if page.exists() else f"Page '{page_title}' does not exist."


def fetch_links(page_title, max_links=10):

    page = wiki_wiki.page(page_title)
    return (
        list(page.links.keys())[:max_links]
        if page.exists()
        else f"Page '{page_title}' does not exist."
    )


def get_page_categories(page_title):

    page = wiki_wiki.page(page_title)
    return (
        [cat for cat in page.categories.keys()]
        if page.exists()
        else f"Page '{page_title}' does not exist."
    )


def get_page_sections(page_title):

    page = wiki_wiki.page(page_title)
    return (
        [section.title for section in page.sections]
        if page.exists()
        else f"Page '{page_title}' does not exist."
    )


def get_page_langlinks(page_title):

    page = wiki_wiki.page(page_title)
    return (
        {lang: page.langlinks[lang].title for lang in page.langlinks}
        if page.exists()
        else f"Page '{page_title}' does not exist."
    )


def search_wikipedia(query, max_results=5):

    return wiki_wiki.search(query, results=max_results) or "No results found."


def get_page_html(page_title):

    page = wiki_wiki.page(page_title)
    return page.text if page.exists() else f"Page '{page_title}' does not exist."


def fetch_random_page():

    import random

    random_page_title = random.choice(wiki_wiki.random(1))
    return random_page_title


def compare_pages(page1, page2):

    return fetch_summary(page1), fetch_summary(page2)


def fetch_interwiki_links(page_title):

    page = wiki_wiki.page(page_title)
    return page.langlinks if page.exists() else f"Page '{page_title}' does not exist."


def fetch_backlinks(page_title):

    page = wiki_wiki.page(page_title)
    return page.backlinks if page.exists() else f"Page '{page_title}' does not exist."


def fetch_redirects(page_title):

    page = wiki_wiki.page(page_title)
    return page.redirects if page.exists() else f"Page '{page_title}' does not exist."


def get_page_views(page_title):

    page = wiki_wiki.page(page_title)
    return page.pageviews if page.exists() else f"Page '{page_title}' does not exist."


def fetch_references(page_title):

    page = wiki_wiki.page(page_title)
    return page.references if page.exists() else f"Page '{page_title}' does not exist."


def find_degrees_of_relation(page1, page2):
    find_degrees_of_relation_bidirectional(page1, page2)
    return f"Degrees of relation between {page1} and {page2}"


@click.group()
def cli():
    pass


@click.command()
@click.argument("page_title")
def summary(page_title):

    click.echo(fetch_summary(page_title))


@click.command()
@click.argument("page_title")
@click.option("--max-links", default=10, help="Max number of links to fetch")
def links(page_title, max_links):

    click.echo(fetch_links(page_title, max_links))


@click.command()
@click.argument("page_title")
def categories(page_title):

    click.echo(get_page_categories(page_title))


@click.command()
@click.argument("page_title")
def sections(page_title):

    click.echo(get_page_sections(page_title))


@click.command()
@click.argument("page_title")
def langlinks(page_title):

    click.echo(get_page_langlinks(page_title))


@click.command()
@click.argument("query")
@click.option("--max-results", default=5, help="Max number of search results to fetch")
def search(query, max_results):

    click.echo(search_wikipedia(query, max_results))


@click.command()
@click.argument("page_title")
def html(page_title):

    click.echo(get_page_html(page_title))


@click.command()
def random_page():

    click.echo(fetch_random_page())


@click.command()
@click.argument("page1")
@click.argument("page2")
def compare(page1, page2):

    click.echo(compare_pages(page1, page2))


@click.command()
@click.argument("page_title")
def backlinks(page_title):

    click.echo(fetch_backlinks(page_title))


@click.command()
@click.argument("page_title")
def pageviews(page_title):

    click.echo(get_page_views(page_title))


cli.add_command(summary)
cli.add_command(links)
cli.add_command(categories)
cli.add_command(sections)
cli.add_command(langlinks)
cli.add_command(search)
cli.add_command(html)
cli.add_command(random_page)
cli.add_command(compare)
cli.add_command(backlinks)
cli.add_command(pageviews)

if __name__ == "__main__":
    cli()
