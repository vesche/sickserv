from sickserv import server_ws
from sickserv.server_ws import response, set_init_key

server_ws.key = 'yellow-submarine'

@server_ws.app.websocket('/test/<sysid>')
async def test(request, ws, sysid):
    data = await ws.recv()
    payload = server_ws.unprocess_payload(sysid, data)
    print('RECV: ' + str(payload))
    return_payload = server_ws.process_payload(sysid, {'Look Mom': 'No Hands!'})
    print('SENT: ' + str(return_payload))
    await ws.send(return_payload)

server_ws.run(port=1337)
