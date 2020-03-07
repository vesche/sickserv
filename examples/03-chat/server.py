#!/usr/bin/env python

import asyncio

from sickserv import server_ws, set_init_key
from sickserv.server_ws import response

set_init_key('yellow-submarine')

CHAT_QUEUE = {
    # sysid: [{sysid: message}]
}


async def _consumer_handler(ws, sysid):
    while True:
        data = await ws.recv()
        payload = server_ws.unprocess_payload(sysid, data)
        message = payload['message']
        for _, queue in CHAT_QUEUE.items():
            queue.append({'sysid': sysid, 'message': message})


async def _producer_handler(ws, sysid):
    if CHAT_QUEUE[sysid]:
        for c in CHAT_QUEUE[sysid]:
            return_payload = server_ws.process_payload(sysid, c)
            await ws.send(return_payload)
        CHAT_QUEUE[sysid] = []
    await asyncio.sleep(.1)


@server_ws.app.websocket('/chat/<sysid>')
async def chat(request, ws, sysid):
    CHAT_QUEUE[sysid] = []

    while True:
        consumer_task = asyncio.ensure_future(_consumer_handler(ws, sysid))
        producer_task = asyncio.ensure_future(_producer_handler(ws, sysid))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()


server_ws.run(port=1337)
