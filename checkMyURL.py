import urllib
import requests
import click
import re
from urllib.request import urlopen
from colorama import init
import bs4
from retry import retry

init()

URL_REGEX = re.compile(
    u"^"
    # protocol identifier
    u"(?:(?:https?|ftp)://)"
    # user:pass authentication
    u"(?:\S+(?::\S*)?@)?"
    u"(?:"
    # IP address exclusion
    # private & local networks
    u"(?!(?:10|127)(?:\.\d{1,3}){3})"
    u"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
    u"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
    u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
    u"|"
    # host name
    u"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
    # domain name
    u"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
    # TLD identifier
    u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
    u")"
    # port number
    u"(?::\d{2,5})?"
    # resource path
    u"(?:/\S*)?"
    u"$"
    , re.UNICODE)


def file_parse(filepath):
    link_list = []
    with open(filepath, 'r') as file_object:
        for link in bs4.BeautifulSoup(file_object.read(), "html.parser", parse_only=bs4.SoupStrainer('a')):
            if link.has_attr('href'):
                link_list.append(link['href'])
    return link_list


def url_parse(base_link):
    link_list = []
    if link_checker(base_link) == 200:
        req = urllib.request.Request(base_link, headers={'User-Agent': "Magic-Browser"})
        page = urlopen(req)
        html = page.read().decode("utf-8")
        soup = bs4.BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a"):
            if link["href"] == '/':
                link_list.append(base_link)
            elif link["href"].startswith("/"):
                link_list.append(base_link[:-1] + link["href"])
            elif link["href"].startswith("http"):
                link_list.append(link["href"])
            else:
                link_list.append(base_link + link["href"])
        return link_list


@retry(ConnectionError, tries=3, delay=2)
def link_checker(link):
    try:
        response = requests.head(link)
        if response.status_code == 200:
            click.secho('[GOOD]    ' + link, fg='green')
        elif response.status_code == 404 or response.status_code == 400:
            click.secho('[BAD]     ' + link, fg='red')
        else:
            click.secho('[UNKNOWN] ' + link, fg='white')
        return response.status_code
    except requests.exceptions.ConnectionError:
        click.secho('[ERROR]   ' + link, fg='red')


@click.command(context_settings={"ignore_unknown_options": True})
@click.option('--parse_url', is_flag=True, help="Will search the link provided for all broken links")
@click.option('--parse_file', is_flag=True, help="Will parse the file provided for broken links")
@click.argument('link')
def main(parse_url, parse_file, link):
    """
    A tool used to determine if a link provided is a valid link or not.
    Either provide the single link or the file needing parsing.
    """
    click.clear()

    if parse_url:
        link_list = url_parse(link)
        if len(link_list) > 1:
            for link in link_list:
                link_checker(link)
        elif len(link_list) == 1:
            link_checker(link_list[0])
        else:
            click.echo("No links on this page")
    elif parse_file:
        click.echo("Parsing file later")
        link_list = file_parse(link)
        for link in link_list:
            if str(link) != 'None':
                link_checker(link)
    else:
        link_checker(link)


if __name__ == "__main__":
    main()
