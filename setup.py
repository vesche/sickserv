#!/usr/bin/env python

import sickserv

from setuptools import setup


setup(
    name='sickserv',
    version=sickserv.__version__,
    author='Austin Jackson',
    author_email='vesche@protonmail.com',
    url='https://github.com/vesche/sickserv',
    description='sickserv',
    license='MIT',
    packages=[
        'sickserv',
    ],
    install_requires=[
        'lz4',
        'sanic',
        'requests',
        'websocket-client',
    ],
    python_requires='>=3',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
        'Topic :: Security',
    ),
)