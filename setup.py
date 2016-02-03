#!/usr/bin/env python

from setuptools import setup, find_packages

setup(  name='demo_delay_scraper',
        version='0.1',
        description='Script to scrape the demo delay site and spit out results in json',
        author='Joe Sislow',
        author_email='chicago@madopal.com',
        install_requires=[
            'requests==2.6.0', 
            'lxml==3.5.0',
            'simplejson==3.8.1',
            'beautifulsoup4==4.4.1'
        ],
)
