import urllib
import requests
import click
import sys
from urllib.request import urlopen
from colorama import init
import bs4
from retry import retry

init()


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
                response_string = '[UNKNOWN] ' + link + '\r\n'
        return response_string, response.status_code
    except requests.exceptions.ConnectionError:
        response_string = ''
        status_code = 400
        if link_filter == 'bad' or link_filter == 'all':
            click.secho('[ERROR]   ' + link, fg='red')
            response_string = '[ERROR]   ' + link + '\r\n'
        return response_string, status_code


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
@click.argument('link')
def main(parse_link, parse_file, save_file, link_filter, link):
    """
    A tool used to determine if a link provided is a valid link or not.
    Either provide the single link or the file needing parsing.
    Only one filter option is allowed at a time.

    Note: if multiple filters are included, only the last one entered will be applied.
    """
    click.clear()
    if parse_link:
        link_list = link_parse(link, link_filter)
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
                file = open('results.txt', 'w+')
            link_list = file_parse(link)
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
    else:
        link_checker(link, link_filter)


if __name__ == '__main__':
    main()
