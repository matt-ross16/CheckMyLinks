from setuptools import setup

setup(
    name='checkMyURL',
    version='0.1',
    description='A link checker',
    author='Matthew Ross',
    author_email='mross20@myseneca.ca',
    install_requires=['click', 'requests', 'colorama', 'bs4', 'retry']
)