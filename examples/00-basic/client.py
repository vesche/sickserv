#!/usr/bin/env python

from sickserv import SickServClient, set_init_key

set_init_key('yellow-submarine')
ssc = SickServClient('127.0.0.1', port=1337)
payload = {
    'endpoint': 'test',
    'example': b'This is some example test data'
}
response = ssc.send(payload)
print(response)
