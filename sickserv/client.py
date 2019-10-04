"""
sickserv.client
"""

import os
import uuid
import requests
import websocket

from .util import process_payload, unprocess_payload

SYSID = str(uuid.uuid1(uuid.getnode(),0))[24:]


class EndpointUndefined(Exception):
    pass


class PayloadNotDict(Exception):
    pass


class WSEndpointNotFound(Exception):
    pass


def check_payload(payload):
    if type(payload) != dict:
        raise PayloadNotDict()
    
    if 'endpoint' not in payload:
        raise EndpointUndefined()

    return payload


class SickServClient:
    def __init__(self, key, server, port=443):
        self.key = key
        self.server = server
        self.port = str(port)
        self.url = 'http://{s}:{p}/'.format(s=self.server, p=self.port)
        self.session = requests.Session()

    def rekey(self, key='', length=16):
        payload = {'endpoint': 'rekey', 'key': key, 'length': str(length)}
        response = self.send(payload)
        self.key = response['key'].decode('utf-8')

    def send(self, payload):
        payload = check_payload(payload)
        endpoint = payload.pop('endpoint')
        enc_payload = process_payload(SYSID, payload, key=self.key)
        url = self.url + endpoint + '/' + SYSID
        response = self.session.request('POST', url, data=enc_payload)
        response.raise_for_status()
        dec_payload = unprocess_payload(SYSID, response.content, key=self.key)
        return dec_payload


class SickServWSClient:
    def __init__(self, key, server, port=443, ws_timeout=1):
        self.key = key
        self.server = server
        self.port = str(port)
        self.ws_timeout = ws_timeout
        self.url = 'ws://{s}:{p}/'.format(s=self.server, p=self.port)
        self.subscriptions = {} # holds websockets for all subs {'rekey': ws, ... }

    def _get_ws(self, endpoint):
        try:
            return self.subscriptions[endpoint]
        except KeyError:
            raise WSEndpointNotFound()

    def _subscribe(self, endpoint):
        if endpoint not in self.subscriptions:
            ws = websocket.WebSocket()
            ws.settimeout(self.ws_timeout)
            ws.connect(self.url + endpoint + '/' + SYSID)
            self.subscriptions[endpoint] = ws

    def _unsubscribe(self, endpoint):
        ws = self._get_ws(endpoint)
        ws.close()
        self.subscriptions.pop(endpoint)

    def rekey(self, key='', length=16):
        payload = {'endpoint': 'rekey', 'key': key, 'length': str(length)}
        self.send(payload)
        response = self.recv('rekey')
        self.key = response['key'].decode('utf-8')

    def send(self, payload):
        payload = check_payload(payload)
        endpoint = payload.pop('endpoint')
        self._subscribe(endpoint)
        enc_payload = process_payload(self.key, payload)
        ws = self._get_ws(endpoint)
        ws.send(enc_payload)

    def recv(self, endpoint):
        ws = self._get_ws(endpoint)
        data = ws.recv()
        return unprocess_payload(self.key, data)
