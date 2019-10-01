"""
sickserv.server_ws
"""

from sanic import Sanic
from sanic import response
from sanic.websocket import WebSocketProtocol

from .util import banner, process_payload, unprocess_payload, gen_random_key

app = Sanic()
key = 'sickservsickserv'


def process(data):
    return process_payload(key, data)


def unprocess(data):
    return unprocess_payload(key, data)


@app.websocket('/rekey')
async def rekey(request, ws):
    data = await ws.recv()
    payload = unprocess(data)

    new_key = payload['key']
    if not new_key:
        new_key = gen_random_key(int(payload['length']))
    return_payload = process({'key': new_key})

    # set new key globally for server
    global key
    key = new_key

    ws.send(return_payload)


def run(port=1337):
    print(banner)
    app.run(host='0.0.0.0', port=port, protocol=WebSocketProtocol)
