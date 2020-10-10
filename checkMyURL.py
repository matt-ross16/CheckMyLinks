import urllib
import requests
import click
import re
import sys
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


# Takes a file passed to it, and passes the links within to link_checker
def file_parse(filepath):
    link_list = []
    try:
        with open(filepath, 'r') as file_object:
            for link in bs4.BeautifulSoup(file_object.read(), "html.parser", parse_only=bs4.SoupStrainer('a')):
                if link.has_attr('href'):
                    link_list.append(link['href'])
        return link_list
    except OSError:
        click.secho('Not a valid file (perhaps try --parse_url)', fg='red')
        error_code = 5
        return error_code


# Takes a link passed to it, and scrapes the webpage for links
def url_parse(base_link, link_filter):
    link_list = []
    error_code = 0
    try:
        if link_checker(base_link, link_filter)[1] == 200:
            req = urllib.request.Request(base_link, headers={'User-Agent': 'Magic-Browser'})
            page = urlopen(req)
            html = page.read().decode('utf-8')
            soup = bs4.BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('a'):
                if link['href'] == '/':
                    link_list.append(base_link)
                elif link['href'].startswith('/'):
                    link_list.append(base_link[:-1] + link['href'])
                elif link['href'].startswith('http'):
                    link_list.append(link['href'])
                else:
                    link_list.append(base_link + link['href'])
            return error_code, link_list
        else:
            click.secho('This link is broken', fg='red')
            error_code = 4
            return error_code
    except requests.exceptions.ConnectionError:
        click.secho('Link Timeout', fg='red')
        error_code = 1
        return error_code
    except requests.exceptions.MissingSchema:
        click.secho('Not a valid URL (perhaps try --parse_file)', fg='red')
        error_code = 2
        return error_code


# Takes a links passed to it, and determines its status
@retry(ConnectionError, tries=3, delay=2)
def link_checker(link, link_filter):
    try:
        response = requests.head(link)
        response_string = ''
        if response.status_code == 200:
            if link_filter == 'good' or link_filter == 'all':
                click.secho('[GOOD]    ' + link, fg='green')
                response_string = '[GOOD]    ' + link + '\r\n'
        elif response.status_code == 404 or response.status_code == 400:
            if link_filter == 'bad' or link_filter == 'all':
                click.secho('[BAD]     ' + link, fg='red')
                response_string = '[BAD]     ' + link + '\r\n'
        else:
            if link_filter == 'unknown' or link_filter == 'all':
                click.secho('[UNKNOWN] ' + link, fg='white')
                response_string = '[UNKNOWN]     ' + link + '\r\n'
        return response_string, response.status_code
    except requests.exceptions.ConnectionError:
        if link_filter == 'bad' or link_filter == 'all':
            click.secho('[ERROR]   ' + link, fg='red')
            response_string = '[ERROR]     ' + link + '\r\n'
            return response_string


@click.command(context_settings={'ignore_unknown_options': True})
@click.option('--parse_url', is_flag=True, help='Will search the link provided for all broken links')
@click.option('--parse_file', is_flag=True, help='Will parse the file provided for broken links')
@click.option('--save_file', is_flag=True,
              help='Will parse the file provided for broken links and save results to a text file')
@click.option('--good_links', 'link_filter', flag_value='good', help='Filter links by only showing GOOD ones')
@click.option('--bad_links', 'link_filter', flag_value='bad', help='Filter links by only showing BAD ones')
@click.option('--unknown_links', 'link_filter', flag_value='unknown', help='Filter links by only showing UNKNOWN ones')
@click.option('--all_links', 'link_filter', flag_value='all', default=True, help='Show all links')
@click.argument('link')
def main(parse_url, parse_file, save_file, link_filter, link):
    """
    A tool used to determine if a link provided is a valid link or not.
    Either provide the single link or the file needing parsing.
    Only one filter option is allowed at a time.

    Note: if multiple filters are included, only the last one entered will be applied.
    """
    click.clear()
    if parse_url:
        link_list = url_parse(link, link_filter)
        if type(link_list) is int:
            error_code = link_list
            sys.exit(error_code)
        elif len(link_list[1]) > 1:
            for link in link_list[1]:
                link_checker(link, link_filter)
        elif len(link_list) == 1:
            link_checker(link_list[0], link_filter)
        else:
            link_checker(link_list[1])
    elif parse_file or save_file:
        try:
            if save_file:
                f = open('results.txt', 'w+')
            link_list = file_parse(link)
            if type(link_list) is int:
                if save_file:
                    f.close()
                error_code = link_list
                sys.exit(error_code)
            else:
                for link in link_list:
                    if str(link) != 'None':
                        result = link_checker(link, link_filter)
                        if save_file:
                            f.write(result[0])
                if save_file:
                    f.close()
        except FileNotFoundError:
            click.secho('This file does not exist in the current directory', fg='red')
            error_code = 3
            sys.exit(error_code)
    else:
        link_checker(link, link_filter)


if __name__ == '__main__':
    main()
