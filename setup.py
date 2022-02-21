#!/usr/bin/env python

import os
from setuptools import setup

directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sickserv',
    version='0.1.3',
    author='Austin Jackson',
    author_email='vesche@protonmail.com',
    url='https://github.com/vesche/sickserv',
    description='sickserv',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=[
        'sickserv',
    ],
    install_requires=[
        'sanic',
        'requests',
        'websocket-client',
    ],
    python_requires='>=3',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Security',
    ),
)
