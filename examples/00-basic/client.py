#!/usr/bin/env python

from sickserv import SickServClient

key = 'yellow-submarine'
payload = {
    'endpoint': 'test',
    'example': b'This is some example test data'
}

ssc = SickServClient(key, '127.0.0.1', port=1337)
response = ssc.send(payload)
print(response)
