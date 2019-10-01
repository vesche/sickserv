from sickserv import server
from sickserv.server import response

server.key = 'yellow-submarine'

@server.app.route('/test', methods=['POST',])
async def test(request):
    payload = server.unprocess(request.body)
    print('RECV: ' + str(payload))
    return_payload = server.process({'Look Mom': 'No Hands!'})
    print('SENT: ' + str(return_payload))
    return response.text(return_payload)

server.run(port=1337)
