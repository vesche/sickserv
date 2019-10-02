# sickserv

This is a Python 3 client/server wrapper to rapidly create fast, encrypted application communication.

* Server is [Sanic](https://github.com/huge-success/sanic) (async) with WebSocket support
* Client uses [requests](https://github.com/psf/requests) or [websocket-client](https://github.com/websocket-client/websocket-client)

## Install

Do it up:

```
$ pip install sickserv --user
```

## Communication Flow

```
Send data:
JSON -> base64 encoded values -> LZ4 compress -> base64 encoded -> RC4 encrypt -> send (HTTPS)

Recv data:
recv (HTTPS) -> RC4 decrypt -> base64 decode -> LZ4 decompress -> base64 decode values -> JSON
```

## Simple Example (non-WebSocket)

Server:
```python
from sickserv import server
from sickserv.server import response, set_init_key

server.set_init_key('yellow-submarine')

@server.app.route('/test/<sysid>', methods=['POST',])
async def test(request, sysid):
    payload = server.unprocess_payload(sysid, request.body)
    print('RECV: ' + str(payload))
    return_payload = server.process_payload(sysid, {'Look Mom': 'No Hands!'})
    print('SENT: ' + str(return_payload))
    return response.text(return_payload)

server.run(port=1337)
```

Client:
```python
from sickserv import SickServClient

key = 'yellow-submarine'
payload = {
    'endpoint': 'test',
    'example': b'This is some example test data'
}

ssc = SickServClient(key, '127.0.0.1', port=1337)
response = ssc.send(payload)
print(response)
```

Server side:
```
$ python3 test_server.py

  _____ ____   __  __  _  _____   ___  ____  __ __
 / ___/|    | /  ]|  |/ ]/ ___/  /  _]|    \|  |  |
(   \_  |  | /  / |  ' /(   \_  /  [_ |  D  )  |  |
 \__  | |  |/  /  |    \ \__  ||    _]|    /|  |  |
 /  \ | |  /   \_ |     \/  \ ||   [_ |    \|  :  |
 \    | |  \     ||  .  |\    ||     ||  .  \\   /
  \___||____\____||__|\_| \___||_____||__|\_| \_/

    v0.0.1 - https://github.com/vesche/sickserv

[2019-09-30 00:58:55 -0500] [34827] [INFO] Goin' Fast @ http://0.0.0.0:1337
[2019-09-30 00:58:55 -0500] [34827] [INFO] Starting worker [34827]
[2019-09-30 00:58:57 -0500] - (sanic.access)[INFO][127.0.0.1:53567]: GET http://127.0.0.1:1337/rekey  200 17
RECV: {'example': b'This is some example test data'}
SENT: 2853CB5398FE8784FEF1DCBD89CC4BAF01AA2661428CD79783D440468504966B01CCD9A5A4E309E342D55EBE4635CDD9D5D78EB98873CAE3D6A7C804A8647CCB1BDD7D32518A112367
[2019-09-30 00:58:57 -0500] - (sanic.access)[INFO][127.0.0.1:53567]: POST http://127.0.0.1:1337/test  200 146
```

Client side:
```
$ python3 test_client.py
{'Look Mom': b'No Hands!'}
```

## Rekey

An initial, matching RC4 key must be supplied. However, the session can easily be rekeyed on the fly.

A rekey is done from the client-end, like so:

```python
ssc.rekey()                       # rekey with a random 16 character length key
ssc.rekey(length=32)              # rekey with a random 32 character length key
ssc.rekey(key='purple-submarine') # rekey with a custom defined key
```
