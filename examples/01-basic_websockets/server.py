from sickserv import server_ws
from sickserv.server_ws import response

server_ws.key = 'yellow-submarine'

@server_ws.app.websocket('/test')
async def test(request, ws):
    data = await ws.recv()
    payload = server_ws.unprocess(data)
    print('RECV: ' + str(payload))
    return_payload = server_ws.process({'Look Mom': 'No Hands!'})
    print('SENT: ' + str(return_payload))
    await ws.send(return_payload)

server_ws.run(port=1337)
