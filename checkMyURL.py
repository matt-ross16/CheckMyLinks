import urllib
import requests
import click
import sys
from urllib.request import urlopen
from colorama import init
import bs4
import re
from retry import retry


init()


# Takes a file passed to it, and passes the links within to link_checker
def file_parse(filepath, ignoreLinks):
    link_list = []
    try:
        with open(filepath, 'r') as file_object:
            for link in bs4.BeautifulSoup(file_object.read(), "html.parser", parse_only=bs4.SoupStrainer('a')):
                linkIgnored = False
                if ignoreLinks:
                    for iLink in ignoreLinks:
                        if len(re.findall(iLink,str(link))) != 0: 
                            linkIgnored = True
                if link.has_attr('href') and linkIgnored == False:
                    link_list.append(link['href'])
        return link_list
    except OSError:
        click.secho('Not a valid file (perhaps try --parse_url)', fg='red')
        error_code = 5
        return error_code


# Takes a file passed to it, and returns the links contained 
def ignore_parse(filepath):
    try:
        fileText = open(filepath, 'r').read()
        fileUrl = set(re.findall('(?!# )(http|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', fileText))
        fileInvalidUrl = set(re.findall('(?!# )(?!http|https)(?!://)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', fileText))
        if fileUrl:
            fileLink = [(url[0]+"://" + url[1] + url[2]) for url in fileUrl]
            return fileLink
        elif fileInvalidUrl:
            click.secho("The URL provided is invalid. Must begin with https:// or http://",fg='red')
            error_code = 5
            sys.exit(error_code)
    except FileNotFoundError as e:
        click.secho('This file does not exist in the current directory', fg='red')
        error_code = 3
        sys.exit(error_code)
    except IOError as e:
        click.secho('This file could not be opened', fg='red')
        error_code = 3
        sys.exit(error_code)


# Parses Telescope blog posts for link status
@retry(ConnectionError, tries=3, delay=2)
def telescope_parse(link_filter):
    # Can also use the Telescope API: 'https://telescope.cdot.systems/posts/'
    base_link = 'http://localhost:3000/posts/'
    link_list = []
    try:
        req = requests.get(base_link, verify=False)
        if (req.status_code != 200):
            click.secho('Not a valid URL')
        else:
            json = req.json()
            for post in json:
                id = post.get('id')
                click.secho(id)
                url = base_link + id
                click.secho(url)
                link_list.append(url)
            return link_list
    except requests.exceptions.SSLError:
        click.secho('An SSL has been encountered', fg='red')


# Takes a link passed to it, and scrapes the webpage for links
def link_parse(base_link, link_filter):
    link_list = []
    error_code = 0
    try:
        if link_checker(base_link, link_filter)[1] == 200:
            url_request = urllib.request.Request(base_link, headers={'User-Agent': 'Magic-Browser'})
            page = urlopen(url_request)
            raw_html = page.read().decode('utf-8')
            html_tags = bs4.BeautifulSoup(raw_html, 'html.parser')
            for link in html_tags.find_all('a'):
                if link['href'] == '/':
                    link_list.append(base_link)
                elif link['href'].startswith('/'):
                    link_list.append(base_link[:-1] + link['href'])
                elif link['href'].startswith('http'):
                    link_list.append(link['href'])
                else:
                    format_link = link['href']
                    link_list.append(format_link[2:-2])
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
                response_string = '[UNKNOWN] ' + link + '\r\n'
        return response_string, response.status_code
    except requests.exceptions.ConnectionError:
        response_string = ''
        status_code = 400
        if link_filter == 'bad' or link_filter == 'all':
            click.secho('[ERROR]   ' + link, fg='red')
            response_string = '[ERROR]   ' + link + '\r\n'
        return response_string, status_code
    except requests.exceptions.MissingSchema:
        response_string = ''
        status_code = 400
        if link_filter == 'bad' or link_filter == 'all':
            click.secho('[ERROR]   ' + link, fg='red')
            response_string = '[ERROR]   ' + link + '\r\n'
        return response_string, status_code


def list_checker(list, link_filter):
    if type(list) is int:
        error_code = list
        sys.exit(error_code)
    elif len(list[1]) > 1:
        for link in list[1]:
            link_checker(link, link_filter)
    elif len(list) == 1:
        link_checker(list[0], link_filter)
    #else:
        #link_checker(list[1], link_filter)


@click.command(context_settings={'ignore_unknown_options': True})
@click.option('-l', '--parse_link', is_flag=True,
              help='Will search the link provided for all broken links')
@click.option('-f', '--parse_file', is_flag=True,
              help='Will parse the file provided for broken links')
@click.option('-s', '--save_file', is_flag=True,
              help='Will parse the file provided for broken links and save results to a text file')
@click.option('-g', '--good_links', 'link_filter', flag_value='good',
              help='Filter links by only showing GOOD ones')
@click.option('-b', '--bad_links', 'link_filter', flag_value='bad',
              help='Filter links by only showing BAD ones')
@click.option('-u', '--unknown_links', 'link_filter', flag_value='unknown',
              help='Filter links by only showing UNKNOWN ones')
@click.option('-a', '--all_links', 'link_filter', flag_value='all', default=True,
              help='Show all links')
@click.option('-i', '--ignore', type=str,
              help='Use file to filter out unwanted URLS')
@click.option('-t', '--telescope', 'telescope', is_flag=True,
              help='Search the 10 most recent posts to Telescope for URLs')
@click.argument('link')
def main(parse_link, parse_file, save_file, link_filter, ignore, telescope, link):
    """
    A tool used to determine if a link provided is a valid link or not.
    Either provide the single link or the file needing parsing.
    Only one filter option is allowed at a time.

    Note: if multiple filters are included, only the last one entered will be applied.
    """
    click.clear()
    if parse_link:
        link_list = link_parse(link, link_filter)
        list_checker(link_list, link_filter)
    elif parse_file or save_file or ignore:
        try:
            ignoreLinks = []
            if save_file:
                file = open('results.txt', 'w+')
            if ignore:
                ignoreLinks = ignore_parse(ignore)
            link_list = file_parse(link,ignoreLinks)
            if type(link_list) is int:
                if save_file:
                    file.close()
                error_code = link_list
                sys.exit(error_code)
            else:
                for link in link_list:
                    if str(link) != 'None':
                        result = link_checker(link, link_filter)
                        if result[0]:
                            if save_file:
                                file.write(result[0])
                if save_file:
                    file.close()
        except FileNotFoundError:
            click.secho('This file does not exist in the current directory', fg='red')
            error_code = 3
            sys.exit(error_code)
    elif telescope:
        telescope_list = telescope_parse(link_filter)
        for link in telescope_list:
            link_list = link_parse(link, link_filter)
            list_checker(link_list, link_filter)
    else:
        link_checker(link, link_filter)


if __name__ == '__main__':
    main()
