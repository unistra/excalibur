#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    lines = requirements.readlines()
    libraries = [lib for lib in lines if not lib.startswith('-')]
    dependency_links = [link.split()[1] for link in lines if
                        link.startswith('-f')]

setup(
    name='excalibur',
    version='1.0.4',
    author='di-dip-unistra',
    author_email='di-dip@unistra.fr',
    maintainer='di-dip-unistra',
    maintainer_email='di-dip@unistra.fr',
    url='https://github.com/unistra/excalibur',
    license='PSF',
    description='A tool to manage plugins',
    long_description=long_description,
    packages=find_packages(),
    download_url='http://pypi.python.org/pypi/excalibur',
    install_requires=libraries,
    dependency_links=dependency_links,
    keywords=['plugins', 'yaml', 'parser'],
    entry_points={},
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3'
    )
)
