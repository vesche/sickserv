"""
sickserv.client
"""

import time
import uuid
import requests
import threading
import websocket

from sickserv.util import process_payload, unprocess_payload, set_key

SYSID = str(uuid.uuid1(uuid.getnode(),0))[24:]
WS_INCOMING = dict()


class EndpointUndefined(Exception):
    pass


class PayloadNotDict(Exception):
    pass


class WSEndpointNotFound(Exception):
    pass


class WSCouldNotConnect(Exception):
    pass


def check_payload(payload):
    """
    Check a payload before processing.
    """
    # ensure payload is a dictionary (for later JSON serialization)
    if type(payload) != dict:
        raise PayloadNotDict(
            f'Payload must be a dictionary, received: {type(payload)}'
        )
    # ensure payload has a mandatory "endpoint" key
    if 'endpoint' not in payload:
        raise EndpointUndefined(
            'You must supply an "endpoint" in the payload!'
        )


class SickServClient:
    """
    sickserv Client, uses requests.
    """
    def __init__(self, server, port=443):
        self.session = requests.Session()
        if port == 443:
            self.base_url = f'https://{server}/'
        else:
            self.base_url = f'http://{server}:{port}/'

    def rekey(self, key='', length=16):
        payload = {'endpoint': 'rekey', 'key': key, 'length': str(length)}
        response = self.send(payload)
        new_key = response['key']
        set_key(SYSID, new_key)

    def send(self, payload):
        # ensure payload is proper
        check_payload(payload)
        endpoint = payload.pop('endpoint')
        # encrypt payload
        enc_payload = process_payload(SYSID, payload)
        # send encrypted payload
        url = self.base_url + endpoint + '/' + SYSID
        response = self.session.request('POST', url, data=enc_payload)
        response.raise_for_status()
        # decrypt response
        dec_payload = unprocess_payload(SYSID, response.content)
        return dec_payload


def ws_on_message(ws, message):
    WS_INCOMING[ws.endpoint].append(unprocess_payload(SYSID, message))


class SickServWSClient:
    """
    sickserv websocket Client, uses websocket-client.
    """
    def __init__(self, server, port=443, ws_timeout=1000, debug=False):
        self.ws_timeout = ws_timeout
        self.url = f'ws://{server}:{port}/'
        self.subscriptions = {} # holds websockets for all subs {'rekey': ws, ... }

        # enable debug mode, ws trace
        if debug:
            websocket.enableTrace(True)

    def _get_ws(self, endpoint):
        try:
            return self.subscriptions[endpoint]
        except KeyError:
            raise WSEndpointNotFound()

    def subscribe(self, endpoint):
        ws = websocket.WebSocketApp(
            self.url + endpoint + '/' + SYSID,
            on_message=ws_on_message
        )
        self.subscriptions[endpoint] = ws
        WS_INCOMING[endpoint] = list()
        ws.endpoint = endpoint
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        # ensure websocket connects
        try:
            conn_timeout = 5
            while not ws.sock.connected and conn_timeout:
                time.sleep(1)
                conn_timeout -= 1
        except AttributeError:
            raise WSCouldNotConnect(
                'Websocket could not be created, server down?'
            )

    def unsubscribe(self, endpoint):
        ws = self._get_ws(endpoint)
        ws.close()
        self.subscriptions.pop(endpoint)
        WS_INCOMING.pop(endpoint)

    def rekey(self, key='', length=16):
        payload = {'endpoint': 'rekey', 'key': key, 'length': str(length)}
        self.subscribe('rekey')
        self.send(payload)

        # ensure rekey success
        attempts = 5
        response = None
        while attempts and not response:
            try:
                response = self.recv('rekey')[0]
            except IndexError:
                time.sleep(1)
                attempts -= 1
                
        # set new key
        new_key = response['key']
        set_key(SYSID, new_key)

    def send(self, payload):
        # ensure payload is proper
        check_payload(payload)
        endpoint = payload.pop('endpoint')
        # encrypt payload
        enc_payload = process_payload(SYSID, payload)
        # get websocket for endpoint
        ws = self._get_ws(endpoint)
        # send encrypted payload
        ws.send(enc_payload)

    def recv(self, endpoint):
        data = WS_INCOMING[endpoint]
        WS_INCOMING[endpoint] = list()
        return data
