#!/usr/bin/env python

import os

from sickserv import SickServClient, set_init_key

set_init_key('yellow-submarine')
ssc = SickServClient('127.0.0.1', port=1337)
payload = {
    'endpoint': 'test',
    'example': {
        'hello': 'world!',
        'stuff': 'and things!'
    },
    'test': ['a','b','c'],
    'binary': os.urandom(32)
}
response = ssc.send(payload)
print(response)
