"""
sickserv.server
"""

from sanic import Sanic
from sanic import response

from .util import banner, process_payload, unprocess_payload, gen_random_key

app = Sanic()
key = 'sickservsickserv'


def process(data):
    return process_payload(key, data)


def unprocess(data):
    return unprocess_payload(key, data)


@app.route('/rekey', methods=['POST',])
async def rekey(request):
    payload = unprocess(request.body)
    new_key = payload['key']
    if not new_key:
        new_key = gen_random_key(int(payload['length']))
    return_payload = process({'key': new_key})

    # set new key globally for server
    global key
    key = new_key

    return response.text(return_payload)


def run(port=1337):
    print(banner)
    app.run(host='0.0.0.0', port=port)
