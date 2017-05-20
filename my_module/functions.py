import base64
from functools import wraps

from Crypto.Cipher import AES


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


class mCrypt(object):
    def __init__(self, key, iv):
        self.aes = AES.new(key, AES.MODE_CBC, iv)

    def encrypt(self, plain_text):
        length = 16
        count = len(plain_text)
        add = length - (count % length)
        plain_text = plain_text + ('\0' * add)
        encrypted_text = self.aes.encrypt(plain_text)
        return base64.b64encode(encrypted_text)

    def decrypt(self, cipher):
        encrypted_text = base64.b64decode(cipher)
        plain_text = self.aes.decrypt(encrypted_text)
        return plain_text.rstrip('\0')


def debug_error(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseException as e:
            print type(e)
            return str(e)

    return decorated_function