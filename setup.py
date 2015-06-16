#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name='django-resticus',
    version='0.0.10',
    author='Derek Payton',
    author_email='derek.payton@gmail.com',
    description='A RESTful framework for Django',
    license='MIT',
    url='https://github.com/dmpayton/django-resticus',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    install_requires=['Django>=1.5', 'six>=1.3.0'],
)
