"""
sickserv.client
"""

import os
import requests
import websocket

from .util import process_payload, unprocess_payload


class WSURINotFound(Exception):
    pass


class EndpointUndefined(Exception):
    pass


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
        try:
            endpoint = payload.pop('endpoint')
        except KeyError:
            raise EndpointUndefined()

        enc_payload = process_payload(self.key, payload)
        response = self.session.request('POST', self.url + endpoint, data=enc_payload)
        dec_payload = unprocess_payload(self.key, response.content)
        return dec_payload


class SickServWSClient:
    def __init__(self, key, server, port=443, ws_timeout=1):
        self.key = key
        self.server = server
        self.port = str(port)
        self.ws_timeout = ws_timeout
        self.url = 'ws://{s}:{p}/'.format(s=self.server, p=self.port)

        self.subs = {} # holds websockets for all subs { ... 'rekey': ws, ... }
        self.subscribe('rekey')

    def _get_ws(self, uri):
        try:
            return self.subs[uri]
        except KeyError:
            raise WSURINotFound()

    def rekey(self, key='', length=16):
        payload = {'endpoint': 'rekey', 'key': key, 'length': str(length)}
        self.send(payload)
        response = self.recv('rekey')
        self.key = response['key'].decode('utf-8')

    def subscribe(self, uri):
        ws = websocket.WebSocket()
        ws.settimeout(self.ws_timeout)
        ws.connect(self.url + uri)
        self.subs[uri] = ws

    def unsubscribe(self, uri):
        ws = self._get_ws(uri)
        ws.close()
        self.subs.pop(uri)

    def send(self, payload):
        try:
            endpoint = payload.pop('endpoint')
        except KeyError:
            raise EndpointUndefined()

        enc_payload = process_payload(self.key, payload)
        ws = self._get_ws(endpoint)
        ws.send(enc_payload)

    def recv(self, uri):
        ws = self._get_ws(uri)
        data = ws.recv()
        return unprocess_payload(self.key, data)
