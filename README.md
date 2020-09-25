# CheckMyLinks
#### A Python based project for checking link status
For those times when you aren't sure if the link you have on hand
actually exists, plug it into this handy tool and you will find the
answer quickly!

## Installation/Getting Started
Before you begin, ensure that you have downloaded Python to your
machine:

    https://www.python.org/downloads/

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

    
## Features
Based on the link that is passed to the program, either a GOOD,
BAD, or UNKNOWN designation will be assigned to the link.
