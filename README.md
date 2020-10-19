[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/matt-ross16/CheckMyLinks.svg)](http://isitmaintained.com/project/matt-ross16/CheckMyLinks "Average time to resolve an issue")
[![Percentage of issues still open](http://isitmaintained.com/badge/open/matt-ross16/CheckMyLinks.svg)](http://isitmaintained.com/project/matt-ross16/CheckMyLinks "Percentage of issues still open")

# CheckMyLinks

#### A Python based project for checking link status

For those times when you aren't sure if the link you have on hand
actually exists, plug it into this handy tool and you will find the
answer quickly!

## Prerequisites

Before you begin, ensure that you have downloaded and installed Python to your
machine:

    https://www.python.org/downloads/

## Installation

To start running this app, be sure to do the following:

    pip3 install --editable .

This will install all the necessary packages for the project.
From there, use the following command to check your link!

    python checkMyURL.py <your URL here>

If you have a URL you would like searched for broken links, try
the --parse_URL option:

    python checkMyURL.py --parse_URL <your URL here>

And if it's a file you want checked for working links, use the
--parse_file option:

    python checkMyURL.py --parse_file <your file here>

And if it's a file you want checked for working links and save the results for later viewing
use the
--save_file option:

    python checkMyURL.py --save_file <your file here>

## Features

Based on the link that is passed to the program, either a GOOD,
BAD, ERROR, or UNKNOWN designation will be assigned to the link.

Filters can be applied to each query to only output links based on
the designation it has (GOOD, BAD, or UNKNOWN). If no filters are applied,
all links will be displayed.
