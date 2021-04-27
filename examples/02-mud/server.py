#!/usr/bin/env python

import random

from sickserv import server, set_init_key
from sickserv.server import response

set_init_key('yellow-submarine')

MAP = [
    ['+', '-', '-', '-', '-', '-', '-', '-', '-', '+', '\n',],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', '\n',],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', '\n',],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', '\n',],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', '\n',],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', '\n',],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', '\n',],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', '\n',],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', '\n',],
    ['+', '-', '-', '-', '-', '-', '-', '-', '-', '+', '\n',],
]
PLAYERS = {
    # sysid: {char': c, 'location': (1, 1), 'chat_queue': ''},
}

def get_map_payload():
    tmp_map = [i[:] for i in MAP]
    for _, player in PLAYERS.items():
        char = player['char']
        x, y = player['location']
        tmp_map[y][x] = char

    m = ''
    for i in tmp_map:
        for j in i:
            m += str(j)
    return m

@server.app.route('/init/<sysid>', methods=['POST',])
async def init(request, sysid):
    payload = server.unprocess_payload(sysid, request.body)
    char = payload['char']
    # random starting location between (1, 1) and (8, 8)
    x, y = random.randint(1, 8), random.randint(1, 8)
    # register character
    PLAYERS[sysid] = {'char': char, 'location': (x, y), 'chat_queue': ''}
    return_payload = server.process_payload(sysid, {'message': get_map_payload()})
    return response.text(return_payload)

@server.app.route('/move/<sysid>', methods=['POST',])
async def move(request, sysid):
    payload = server.unprocess_payload(sysid, request.body)
    direction = payload['direction']
    x, y = PLAYERS[sysid]['location']

    if direction == 'north':
        my, mx = y - 1, x
    elif direction == 'south':
        my, mx = y + 1, x
    elif direction == 'east':
        my, mx = y, x + 1
    elif direction == 'west':
        my, mx = y, x - 1

    if MAP[my][mx] in ['+', '-', '|']:
        return_payload = server.process_payload(
            sysid, {'message': 'You cannot move that way!'}
        )
    else:
        PLAYERS[sysid]['location'] = (mx, my)
        return_payload = server.process_payload(
            sysid, {'message': f'You moved {direction}!'}
        )
    return response.text(return_payload)

@server.app.route('/chat/<sysid>', methods=['POST',])
async def chat(request, sysid):
    payload = server.unprocess_payload(sysid, request.body)
    text_message = payload['text']
    for _, player in PLAYERS.items():
        player['chat_queue'] += f'{player["char"]} says: {text_message}\n'
    chat_queue = PLAYERS[sysid]['chat_queue']
    PLAYERS[sysid]['chat_queue'] = ''
    return_payload = server.process_payload(sysid, {'message': chat_queue})
    return response.text(return_payload)

@server.app.route('/look/<sysid>', methods=['POST',])
async def look(request, sysid):
    return_payload = server.process_payload(sysid, {'message': get_map_payload()})
    return response.text(return_payload)

@server.app.route('/logout/<sysid>', methods=['POST',])
async def logout(request, sysid):
    PLAYERS.pop(sysid)
    return_payload = server.process_payload(sysid, {'message': 'logout'})
    return response.text(return_payload)

server.run(port=1337)
