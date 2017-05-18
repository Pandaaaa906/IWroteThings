import base64
import urllib2
import json

import logging
from google.appengine.api import memcache
from auth.models import User
from flask import Flask, jsonify, redirect
from flask import request
from functools import wraps
from functions.WXBizDataCrypt import WXBizDataCrypt
from Crypto.Cipher import AES

app = Flask(__name__)
app.config['app_id'] = "wxc2794b66adfdb911"
app.config['app_secret'] = "cbf3448395b6129dd4b08ed3b057ad7d"
app.config['SECRET_KEY'] = '\x14\x02\xacQ{\x17I\xbbU\xe1\xe1\xf2`\x05\x0fS\xd4\x0eC\x8d)\xa4\xe6\xb6'
# os.urandom(16)
app.config["mKEY"] = '\x8d\x95]\x03\xc9\xff[h\x98\xc3b\xcf\xfa\xfd\xa2\xd0'
app.config["mIV"] = '\x9f\xd1\xca\xb4\x1e=+\xa5\x82\x1be=\x83\x03\xa3\xca'


class mCrypt(object):
    def __init__(self):
        self.aes = AES.new(app.config["mKEY"], AES.MODE_CBC, app.config["mIV"])

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


def check_wx_referer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        referer = request.headers.get('referer', "")
        app_id = app.config.get('app_id', "")
        st = "https://servicewechat.com/{appid}".format(appid=app_id)
        if not referer.startswith(st):
            return "You're Not My Little App"
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/wx/login', methods=["GET", "POST"])
# @check_wx_referer
def login():
    open_id = request.args.get("open_id")
    mAES = mCrypt()
    open_id = mAES.decrypt(open_id)
    session_key = memcache.get(open_id, None)
    if session_key is None:
        return jsonify(status="fail", msg="Session Lost Please re-Login")
    else:
        app_id = app.config.get('app_id', None)
        j_request = request.get_json()
        encryptedData = j_request.get('encryptedData')
        iv = j_request.get('iv')
        pc = WXBizDataCrypt(app_id, session_key)
        obj = pc.decrypt(encryptedData, iv)
        obj.pop("watermark")
        try:
            user = User(**obj)
            user.put()
        except BaseException as e:
            print e
        return jsonify(obj)
        # TODO check&add user to database


@app.route('/wx/get_session')
# @check_wx_referer
def get_session():
    js_code = request.args.get('js_code', '')
    app_id = app.config.get('app_id', None)
    app_secret = app.config.get('app_secret', None)
    url = "https://api.weixin.qq.com/sns/jscode2session?appid={app_id}&secret={app_secret}&js_code={js_code}&grant_type=authorization_code"
    response = urllib2.urlopen(url.format(app_id=app_id, app_secret=app_secret, js_code=js_code))
    j_obj = json.loads(response.read())
    errcode = j_obj.get("errcode", None)
    if errcode is not None:
        msg = j_obj.get("errmsg", None)
        return jsonify(status="fail", errcode=errcode, msg=msg)
    else:
        open_id = j_obj.get("openid", "None")
        session_key = j_obj.get("session_key", "None")
        expires_in = j_obj.get("expires_in", 1500)
        memcache.set(open_id, session_key, expires_in)
        mAES = mCrypt()
        en_open_id = mAES.encrypt(open_id)
        return jsonify(status="success", open_id=en_open_id)


"""
@app.route('/auto/<app>/<ctrl>/<pk>')
def rout_handler(app, ctrl, pk):
    return 'Under Construct'
"""

if __name__ == '__main__':
    # session.permanent = True
    # app.secret_key = '\x14\x02\xacQ{\x17I\xbbU\xe1\xe1\xf2`\x05\x0fS\xd4\x0eC\x8d)\xa4\xe6\xb6'
    app.run(debug=True)
