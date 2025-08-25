#!/usr/bin/python

import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

KEYWORDS = ('stun client')

setuptools.setup(
    name="aiostun",
    version="0.6.0",
    author="Denis MACHARD",
    author_email="d.machard@gmail.com",
    description="Asynchronous STUN client for Python with UDP, TCP and TLS support",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/dmachard/python-aiostun",
    packages=['aiostun', 'tests'],
    include_package_data=True,
    platforms='any',
    keywords=KEYWORDS,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=[]
)