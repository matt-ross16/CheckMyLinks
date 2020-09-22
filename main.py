import requests
import click
import re

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


def link_checker(link):
    response = requests.head(link)
    return response.status_code
    # print(response.status_code)


@click.command()
@click.argument('link')
def main(link):
    """
    A tool used to determine if a link provided is a valid link or not.
    Either provide the single link or the file needing parsing.
    """
    click.clear()
    links_list = re.findall(URL_REGEX, link)
    if links_list:
        print('Links were found')
        print(links_list)
        for link in links_list:
            if link_checker(link) == 200:
                click.secho('[GOOD] ' + link, color='green')
            elif link_checker(link) == 404:
                click.secho('[BAD] ' + link, fg='red')
            else:
                click.secho('[UNKNOWN] ' + link, fg='gray')
    else:
        print('No links found')


if __name__ == "__main__":
    main()
