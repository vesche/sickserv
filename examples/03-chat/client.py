#!/usr/bin/env python

import sys
import time
import threading

from string import printable
from blessed import Terminal
from sickserv import SickServWSClient, set_init_key

set_init_key('yellow-submarine')
ssc = SickServWSClient('127.0.0.1', port=1337)
term = Terminal()
print(term.clear + 'sickserv chat :)')
messages = []


def draw_prompt():
    with term.location(0, term.height):
        print('> ' + ' '*(term.width-2), end='')


def print_messages():
    scroll_up = term.height-1
    for message in messages[::-1]:
        scroll_up -= 1
        if scroll_up:
            with term.location(0, scroll_up):
                print(term.clear_eol + message)
        else: break


def recv_chat():
    while True:
        response = ssc.recv('chat')
        if not response:
            time.sleep(.1)
            continue
        for r in response:
            messages.append(r['sysid'] + ': ' + r['message'])
        print_messages()


def ssc_connect():
    print('Connecting...')
    ssc.subscribe(endpoint='chat')
    t = threading.Thread(target=recv_chat)
    t.daemon = True
    t.start()
    print('Connected!')


def main():
    msg = str()
    msglen = 2
    draw_prompt()

    while True:
        with term.cbreak():
            user_input = term.inkey()

        if repr(user_input) == 'KEY_ENTER':
            if msg == '/rekey':
                ssc.rekey()
            elif msg == '/quit':
                ssc.unsubscribe('chat')
                sys.exit(0)
            else:
                payload = {'endpoint': 'chat', 'message': msg}
                ssc.send(payload)
            msg = str()
            msglen = 2
            draw_prompt()
            continue

        if repr(user_input) == 'KEY_BACKSPACE':
            if msglen <= 2:
                continue
            with term.location(msglen-1, term.height):
                print(' ', end='')
            msg = msg[:-1]
            msglen -= 1
            continue

        if user_input in list(printable):
            with term.location(msglen, term.height):
                print(user_input, end='')
                msg += user_input
                msglen += 1


if __name__ == '__main__':
    ssc_connect()
    print('/rekey - Rekey session.\n/quit - Quit chat.')
    main()
