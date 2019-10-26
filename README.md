# sickserv

This is a Python 3 client/server wrapper & framework to rapidly create fast, encrypted, asynchronous, multi-client applications.

* Server is [Sanic](https://github.com/huge-success/sanic) (async) with WebSocket support
* Client uses [requests](https://github.com/psf/requests) or [websocket-client](https://github.com/websocket-client/websocket-client)

## Install

Do it up:
```
$ pip install sickserv --user
```

## Communication Flow

Initial payloads are always JSON (with a defined endpoint), which are then base64 encoded, RC4 encrypted, and then sent over HTTP or HTTPS (on any port desired).

```
Send data:
JSON -> base64 encode values -> RC4 encrypt -> send (HTTPS)

Recv data:
recv (HTTPS) -> RC4 decrypt -> base64 decode values -> JSON
```

## Simple Example (non-WebSocket)

See the `examples/` folder for more, including: a MUD, chat server, and reverse shell.

Server:
```python
from sickserv import server, set_init_key
from sickserv.server import response

set_init_key('yellow-submarine')

@server.app.route('/test/<sysid>', methods=['POST',])
async def test(request, sysid):
    payload = server.unprocess_payload(sysid, request.body)
    print(payload)
    return_payload = server.process_payload(sysid, {'Look Mom': 'No Hands!'})
    return response.text(return_payload)

server.run(port=1337)
```

Client:
```python
from sickserv import SickServClient, set_init_key

set_init_key('yellow-submarine')
ssc = SickServClient('127.0.0.1', port=1337)
payload = {
    'endpoint': 'test',
    'example': 'This is some example test data'
}
response = ssc.send(payload)
print(response)
```

Server side:
```
$ python server.py

  _____ ____   __  __  _  _____   ___  ____  __ __ 
 / ___/|    | /  ]|  |/ ]/ ___/  /  _]|    \|  |  |
(   \_  |  | /  / |  ' /(   \_  /  [_ |  D  )  |  |
 \__  | |  |/  /  |    \ \__  ||    _]|    /|  |  |
 /  \ | |  /   \_ |     \/  \ ||   [_ |    \|  :  |
 \    | |  \     ||  .  |\    ||     ||  .  \\   / 
  \___||____\____||__|\_| \___||_____||__|\_| \_/  

    v0.1.0 - https://github.com/vesche/sickserv 

[2019-10-26 06:12:47 -0500] [31313] [INFO] Goin' Fast @ http://0.0.0.0:1337
[2019-10-26 06:12:47 -0500] [31313] [INFO] Starting worker [31313]
{'example': 'This is some example test data'}
[2019-10-26 06:12:57 -0500] - (sanic.access)[INFO][127.0.0.1:41550]: POST http://127.0.0.1:1337/test/b0610ba87aa2  200 60
```

Client side:
```
$ python test_client.py
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
