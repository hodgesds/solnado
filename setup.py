# -*- coding: utf-8 -*-
from os.path import join, dirname
from setuptools import setup, find_packages
import sys
import os

VERSION = (0, 9, 3)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

f = open(join(dirname(__file__), 'README.rst'))
long_description = f.read().strip()
f.close()

install_requires = [
    'tornado>=3.2',
]
tests_require = [
    'nose',
    'coverage',
    'mock',
    'nosexcover',
    'tornado>=3.2.2',
]

# use external unittest for 2.6
if sys.version_info[:2] == (2, 6):
    install_requires.append('unittest2')
    install_requires.append('argparse')

setup(
    name             = 'solnado',
    description      = "Tornado HTTP client for Solr",
    license          = "Apache License, Version 2.0",
    url              = "https://github.com/hodgesds/solnado",
    long_description = long_description,
    version          = __versionstr__,
    author           = "Daniel Hodges",
    author_email     = "hodges.daniel.scott@gmail.com",
    scripts          = ['bin/solnado'],
    packages         = find_packages(
        where        = '.',
        exclude      = ('tests*', 'bin*')
    ),
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Text Processing :: Indexing",
    ],
    install_requires=install_requires,

    test_suite='tests.run_tests.run_all',
    tests_require=tests_require,
)
