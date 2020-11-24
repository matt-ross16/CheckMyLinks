[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/matt-ross16/CheckMyLinks.svg)](http://isitmaintained.com/project/matt-ross16/CheckMyLinks "Average time to resolve an issue")
[![Percentage of issues still open](http://isitmaintained.com/badge/open/matt-ross16/CheckMyLinks.svg)](http://isitmaintained.com/project/matt-ross16/CheckMyLinks "Percentage of issues still open")

# CheckMyLinks

#### A Python based project for checking link status

For those times when you aren't sure if the link you have on hand
actually exists, plug it into this handy tool and you will find the
answer quickly!

Use the following command to check your link!

    python checkMyURL.py <your link here>

If you have a URL you would like searched for broken links, try
the -l or --parse_link option:

    python checkMyURL.py -l <your link here>

    python checkMyURL.py --parse_link <your link here>

And if it's a file you want checked for working links, use the -f or
--parse_file option:

    python checkMyURL.py -f <your file here>

    python checkMyURL.py --parse_file <your file here>

And if it's a file you want checked for working links and save the results for later viewing
use the -s or --save_file option:

    python checkMyURL.py -s <your file here>
    
    python checkMyURL.py --save_file <your file here>

## Features

Based on the link that is passed to the program, either a GOOD,
BAD, ERROR, or UNKNOWN designation will be assigned to the link.

Filters can be applied to each query to only output links based on
the designation it has (GOOD, BAD, or UNKNOWN). If no filters are applied,
all links will be displayed.

For GOOD links, use -g or --good_links:

    python checkMyURL.py -g -l <your link here>
    
    python checkMyURL.py --good_links -l <your link here>


For BAD links, use -b or --bad_links:

    python checkMyURL.py -b -l <your link here>

    python checkMyURL.py --bad_links -l <your link here>


For UNKNOWN links, use -u or --unknown_links:

    python checkMyURL.py -u -l <your link here>

    python checkMyURL.py --unknown_links -l <your link here>


For all links, use -a or --all_links:

    python checkMyURL.py -a -l <your link here>

    python checkMyURL.py --all_links -l <your link here>

If you would link to include a file containing links to ignore: 
  
    python checkMyURL.py  <your file here> -i <your ignore file here>
    
Note: the ignore file should be formatted with only comments and http:// or https:// links

To run the link checker against the Telescope API, use:

    python checkMyURL.py -t -a .

Note: the period is used as a placeholder for a filename.