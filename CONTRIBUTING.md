## Prerequisites

Before you begin, ensure that you have downloaded and installed Python to your
machine:

    https://www.python.org/downloads/

## Installation

Begin by cloning the repo:

    git clone https://github.com/matt-ross16/CheckMyLinks.git

To start running this app, be sure to do the following:

    pip3 install --editable .

This will install all the necessary packages for the project.

## Formatting

The formatter used to standardize this program is [Black](https://pypi.org/project/black/).

Be sure to run this formatter prior to creating a pull request:

    format.sh

## Linting

The linter used to catch errors for this program is [Flake8](https://flake8.pycqa.org/en/latest/index.html).

To run this linter:

    lint.sh