from setuptools import setup

setup(
    name='main',
    version='0.1',
    description='A link checker',
    author='Matthew Ross',
    author_email='mross20@myseneca.ca',
    packages=['main'],
    install_requires=['click', 'requests']
)