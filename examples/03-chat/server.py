
from sickserv import server_ws, set_init_key
from sickserv.server_ws import response

set_init_key('yellow-submarine')

CHAT_QUEUE = {
    # sysid: [{sysid: message}]
}

@server_ws.app.websocket('/init/<sysid>')
async def init(request, ws, sysid):
    while True:
        await ws.recv()
        CHAT_QUEUE[sysid] = []

@server_ws.app.websocket('/send/<sysid>')
async def chat(request, ws, sysid):
    while True:
        data = await ws.recv()
        payload = server_ws.unprocess_payload(sysid, data)
        message = payload['message']
        for _, queue in CHAT_QUEUE.items():
            queue.append({'sysid': sysid, 'message': message})

@server_ws.app.websocket('/queue/<sysid>')
async def queue(request, ws, sysid):
    while True:
        await ws.recv()
        print(CHAT_QUEUE)
        if CHAT_QUEUE[sysid]:
            for c in CHAT_QUEUE[sysid]:
                return_payload = server_ws.process_payload(sysid, c)
                await ws.send(return_payload)
            CHAT_QUEUE[sysid] = []

server_ws.run(port=1337)
