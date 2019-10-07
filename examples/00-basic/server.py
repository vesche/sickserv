from sickserv import server, set_init_key
from sickserv.server import response

set_init_key('yellow-submarine')

@server.app.route('/test/<sysid>', methods=['POST',])
async def test(request, sysid):
    payload = server.unprocess_payload(sysid, request.body)
    print('RECV: ' + str(payload))
    return_payload = server.process_payload(sysid, {'Look Mom': 'No Hands!'})
    print('SENT: ' + str(return_payload))
    return response.text(return_payload)

server.run(port=1337)
