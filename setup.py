#!/usr/bin/env python

from setuptools import setup

__version__ = '0.1.1'

setup(
    name='sickserv',
    version=__version__,
    author='Austin Jackson',
    author_email='vesche@protonmail.com',
    url='https://github.com/vesche/sickserv',
    description='sickserv',
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
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
        'Topic :: Security',
    ),
)
