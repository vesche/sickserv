#!/usr/bin/env python

from sickserv import SickServWSClient

key = 'yellow-submarine'
payload = {
    'endpoint': 'test',
    'example': b'This is some example test data'
}

ssc = SickServWSClient(key, '127.0.0.1', port=1337)
ssc.send(payload)
response = ssc.recv('test')
print(response)
