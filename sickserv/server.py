"""
sickserv.server
"""

from sanic import Sanic
from sanic import response

from sickserv.util import (
    process_payload, unprocess_payload,
    BANNER, gen_random_key, set_key, set_init_key
)

app = Sanic()


@app.route('/rekey/<sysid>', methods=['POST',])
async def rekey(request, sysid):
    """
    Handle a client rekey request.
    """
    payload = unprocess_payload(sysid, request.body)

    new_key = payload['key']
    if not new_key:
        new_key = gen_random_key(int(payload['length']))
    return_payload = process_payload(sysid, {'key': new_key})

    # set new key globally for server
    set_key(sysid, new_key)

    return response.text(return_payload)


def run(port=1337):
    """
    Start sanic server listening globally on a given port.
    """
    print(BANNER)
    app.run(host='0.0.0.0', port=port)
