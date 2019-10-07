#!/usr/bin/env python

import time
from sickserv import SickServWSClient, set_init_key

set_init_key('yellow-submarine')
ssc = SickServWSClient('127.0.0.1', port=1337)

ssc.subscribe(endpoint='test')
payload = {
    'endpoint': 'test',
    'example': b'This is some example test data'
}
ssc.send(payload)

response = None
while not response:
    response = ssc.recv('test')
    time.sleep(1)
print(response)
