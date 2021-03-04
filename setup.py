#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='BluenetTestSuite',
    version='0.1',
    packages=find_packages(exclude=["notebooks"]),
    author="Crownstone B.V.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crownstone/bluenet-test-suite",
    install_requires=list(package.strip() for package in open('requirements.txt')),
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ],
    python_requires='>=3.7',
)