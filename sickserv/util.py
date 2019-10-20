"""
sickserv.util
"""

import json
import base64
import random

from string import ascii_lowercase as alphabet
from sickserv.rc4 import encrypt as rc4_encrypt
from sickserv.rc4 import decrypt as rc4_decrypt

BANNER = r"""
  _____ ____   __  __  _  _____   ___  ____  __ __ 
 / ___/|    | /  ]|  |/ ]/ ___/  /  _]|    \|  |  |
(   \_  |  | /  / |  ' /(   \_  /  [_ |  D  )  |  |
 \__  | |  |/  /  |    \ \__  ||    _]|    /|  |  |
 /  \ | |  /   \_ |     \/  \ ||   [_ |    \|  :  |
 \    | |  \     ||  .  |\    ||     ||  .  \\   / 
  \___||____\____||__|\_| \___||_____||__|\_| \_/  

    v{ver} - {url} 
""".format(ver='0.0.7', url='https://github.com/vesche/sickserv')
INIT_KEY = 'sickservsickserv'
KEY_TABLE = {}


def base64_encode(data):
    if type(data) == str:
        data = str.encode(data)
    return base64.encodebytes(data).decode('utf-8')


def base64_decode(data):
    if type(data) == str:
        data = str.encode(data)
    return base64.decodebytes(data).decode('utf-8')


class DecryptionError(Exception):
    pass


def iter_payload(payload, encode_mode):
    for k, v in payload.items():
        if isinstance(v, dict):
            iter_payload(v, encode_mode=encode_mode)
        elif isinstance(v, list):
            if encode_mode:
                payload[k] = [base64_encode(i) for i in v]
            else:
                payload[k] = [base64_decode(i) for i in v]
        else:
            if encode_mode:
                payload[k] = base64_encode(v)
            else:
                payload[k] = base64_decode(v)
    return payload


def prep_payload(payload):
    return json.dumps(iter_payload(payload, encode_mode=True))


def unprep_payload(payload):
    return iter_payload(json.loads(payload), encode_mode=False)


def process_payload(sysid, payload, key=None):
    # lookup key if none given
    if not key:
        key = get_key(sysid)
    # prep payload and rc4 encrypt
    return rc4_encrypt(key, prep_payload(payload))


def unprocess_payload(sysid, payload, key=None):
    # lookup key if none given
    if not key:
        key = get_key(sysid)
    # rc4 decrypt
    try:
        decrypted_payload = rc4_decrypt(key, payload)
    except UnicodeDecodeError:
        raise DecryptionError('Could not decrypt payload, wrong key?')
    # unprep payload
    return unprep_payload(decrypted_payload)


def gen_random_key(length=16):
    return ''.join([random.choice(alphabet) for _ in range(length)])


class SysIDNotFound(Exception):
    pass


def get_key(sysid):
    if sysid not in KEY_TABLE:
        KEY_TABLE[sysid] = INIT_KEY
        return INIT_KEY
    try:
        return KEY_TABLE[sysid]
    except KeyError:
        raise SysIDNotFound()


def set_key(sysid, new_key):
    KEY_TABLE[sysid] = new_key


def set_init_key(init_key):
    global INIT_KEY
    INIT_KEY = init_key
