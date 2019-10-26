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
""".format(ver='0.1.0', url='https://github.com/vesche/sickserv')
INIT_KEY = 'sickservsickserv'
KEY_TABLE = {}


def base64_encode(data):
    """
    base64 encode data, will convert given strings to bytes.
    Returns base64 encoded string.
    """
    if type(data) == str:
        data = str.encode(data)
    return base64.encodebytes(data).decode('utf-8')


def base64_decode(data):
    """
    base64 decode data, will convert given strings to bytes.
    Returns base64 decoded value as a string or bytes as appropriate.
    """
    if type(data) == str:
        data = str.encode(data)
    try:
        return base64.decodebytes(data).decode('utf-8')
    except UnicodeDecodeError:
        return base64.decodebytes(data)


class DecryptionError(Exception):
    pass


class InvalidPayloadType(Exception):
    pass


def iter_payload(payload, encode_mode):
    """
    Iterate thru payload to encode or decode values.
    Handles nested dicts, flat lists, strings, bytes, and invalid types.
    """
    for k, v in payload.items():
        # handle nested dictionary, recursive function
        if isinstance(v, dict):
            iter_payload(v, encode_mode=encode_mode)
        # handle flat lists
        elif isinstance(v, list):
            if encode_mode:
                payload[k] = [base64_encode(i) for i in v]
            else:
                payload[k] = [base64_decode(i) for i in v]
        # handle strings and bytes
        elif isinstance(v, str) or isinstance(v, bytes):
            if encode_mode:
                payload[k] = base64_encode(v)
            else:
                payload[k] = base64_decode(v)
        # raise on any other type
        else:
            raise InvalidPayloadType(
                f'Cannot base64 encode {type(v)}, given: {v}'
            )
    return payload


def prep_payload(payload):
    """
    base64 encodes payload values and returns as a serialized JSON string.
    """
    return json.dumps(iter_payload(payload, encode_mode=True))


def unprep_payload(payload):
    """
    Loads JSON payload, base64 decodes values and returns as a dict.
    """
    return iter_payload(json.loads(payload), encode_mode=False)


def process_payload(sysid, payload, key=None):
    """
    RC4 encrypts the 'prepared' payload.
    """
    # lookup key if none given
    if not key:
        key = get_key(sysid)
    # prep payload and rc4 encrypt
    return rc4_encrypt(key, prep_payload(payload))


def unprocess_payload(sysid, payload, key=None):
    """
    RC4 decrypts the 'unprepared' payload.
    """
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
    """
    Returns a random n-length comprised of the 26 letters of the alphabet.
    Default is 16 characters in length.
    """
    return ''.join([random.choice(alphabet) for _ in range(length)])


class SysIDNotFound(Exception):
    pass


def get_key(sysid):
    """
    Get RC4 key from the global KEY_TABLE given a sysid.
    Will set the sysid key to INIT_KEY if sysid not present in KEY_TABLE.
    """
    if sysid not in KEY_TABLE:
        set_key(sysid, INIT_KEY)
        return INIT_KEY
    try:
        return KEY_TABLE[sysid]
    except KeyError:
        raise SysIDNotFound()


def set_key(sysid, new_key):
    """
    Set a new key for a sysid in the KEY_TABLE.
    """
    KEY_TABLE[sysid] = new_key


def set_init_key(init_key):
    """
    Set the global INIT_KEY.
    """
    global INIT_KEY
    INIT_KEY = init_key
