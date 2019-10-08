#!/usr/bin/env python

import sys
from sickserv import SickServClient, set_init_key

set_init_key('yellow-submarine')
ssc = SickServClient('127.0.0.1', port=1337)

BANNER = """sickserv MUD
~~~~~~~~~~~~~~~~~~~~~~~~
look                     ---> look around
north, south, east, west ---> move around
chat Hello, friends!     ---> say something
logout                   ---> disconnect
"""

def main():
    user_input = input('> ')

    try:
        command = user_input.split()[0].lower()
    except IndexError:
        return None
    try:
        args = ' '.join(user_input.split()[1:])
    except IndexError:
        args = None

    if command in ['north', 'south', 'east', 'west']:
        payload = {'endpoint': 'move', 'direction': command}
    elif command == 'chat':
        payload = {'endpoint': 'chat', 'text': args}
    elif command == 'look':
        payload = {'endpoint': 'look'}
    elif command == 'logout':
        payload = {'endpoint': 'logout'}
    else:
        return None

    response = ssc.send(payload)
    message = response['message'].decode('utf-8')
    if message == 'logout':
        sys.exit(0)
    print(message)

if __name__ == '__main__':
    print(BANNER)
    c = input('What would you like your character letter to be (one letter)? ')
    payload = {'endpoint': 'init', 'char': c}
    response = ssc.send(payload)
    print(response['message'].decode('utf-8'))

    while True:
        main()
