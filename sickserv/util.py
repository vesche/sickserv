"""
sickserv.util
"""

import json
import base64
import random
import lz4.frame

from .rc4 import encrypt, decrypt
from string import ascii_lowercase as alphabet

BANNER = r"""
  _____ ____   __  __  _  _____   ___  ____  __ __ 
 / ___/|    | /  ]|  |/ ]/ ___/  /  _]|    \|  |  |
(   \_  |  | /  / |  ' /(   \_  /  [_ |  D  )  |  |
 \__  | |  |/  /  |    \ \__  ||    _]|    /|  |  |
 /  \ | |  /   \_ |     \/  \ ||   [_ |    \|  :  |
 \    | |  \     ||  .  |\    ||     ||  .  \\   / 
  \___||____\____||__|\_| \___||_____||__|\_| \_/  

    v{ver} - {url} 
""".format(ver='0.0.5', url='https://github.com/vesche/sickserv')
INIT_KEY = 'sickservsickserv'
KEY_TABLE = {}


def base64_encode(data):
    return base64.encodebytes(data).decode('utf-8')


def base64_decode(data):
    return base64.decodebytes(data)


def lz4_compress(data):
    return lz4.frame.compress(data)


def lz4_decompress(data):
    return lz4.frame.decompress(data)


def rc4_encrypt(key, data):
    return encrypt(key, data)


def rc4_decrypt(key, data):
    return str.encode(decrypt(key, data))


class DecryptionError(Exception):
    pass


def prep_payload(payload):
    """
    base64 encode data, utf-8 decode, return json as bytes
    """
    # this is assuming the dict is flat
    for k, v in payload.items():
        if type(v) == str:
            v = str.encode(v)
        payload[k] = base64_encode(v)

    json_payload = json.dumps(payload)
    return str.encode(json_payload)


def unprep_payload(payload):
    dict_payload = json.loads(payload)
    for k, v in dict_payload.items():
        dict_payload[k] = base64_decode(str.encode(v)).decode('utf-8')
    return dict_payload


def process_payload(sysid, payload, key=None):
    # lookup key if none given
    if not key:
        key = get_key(sysid)

    # prep payload -> lz4 compress -> base64 encode -> rc4 encrypt
    return rc4_encrypt(key, base64_encode(lz4_compress(prep_payload(payload))))


def unprocess_payload(sysid, payload, key=None):
    # lookup key if none given
    if not key:
        key = get_key(sysid)
    # rc4 decrypt
    try:
        decrypted_payload = rc4_decrypt(key, payload)
    except UnicodeDecodeError:
        raise DecryptionError('Could not decrypt payload, wrong key?')

    # base64 decode -> lz4 decompress -> unprep payload
    return unprep_payload(lz4_decompress(base64_decode(decrypted_payload)))


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
