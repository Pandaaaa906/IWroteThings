import urllib2
import json
from google.appengine.api import memcache
from flask import Flask, jsonify, session
from flask import request
from functools import wraps
from functions.WXBizDataCrypt import WXBizDataCrypt

app = Flask(__name__)
app.config['app_id'] = "wxc2794b66adfdb911"
app.config['app_secret'] = "cbf3448395b6129dd4b08ed3b057ad7d"
app.config['SECRET_KEY'] = '\x14\x02\xacQ{\x17I\xbbU\xe1\xe1\xf2`\x05\x0fS\xd4\x0eC\x8d)\xa4\xe6\xb6'


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
def hello_world():
    return 'Hello World!'


@app.route('/wx/login', methods=["GET", "POST"])
@check_wx_referer
def login():
    app_id = app.config.get('app_id', None)
    j_request = request.get_json()
    # userInfo = j_request.get("userInfo")
    open_id = request.args.get("open_id")
    session_key = memcache.get(open_id)
    encryptedData = j_request.get('encryptedData')
    iv = j_request.get('iv')
    pc = WXBizDataCrypt(app_id, session_key)
    obj = pc.decrypt(encryptedData, iv)
    return jsonify(obj)
    # TODO check&add user to database


@app.route('/wx/get_session_key')
# @check_wx_referer
def get_session_key():
    js_code = request.args.get('js_code', '')
    app_id = app.config.get('app_id', None)
    app_secret = app.config.get('app_secret', None)
    url = "https://api.weixin.qq.com/sns/jscode2session?appid={app_id}&secret={app_secret}&js_code={js_code}&grant_type=authorization_code"
    response = urllib2.urlopen(url.format(app_id=app_id, app_secret=app_secret, js_code=js_code))
    j_obj = json.loads(response.read())
    errcode = j_obj.get("errcode", None)
    if errcode:
        msg = j_obj.get("errmsg", None)
        return jsonify(status="fail", errcode=errcode, msg=msg)
    else:
        open_id = j_obj.get("openid", "None")
        session_key = j_obj.get("session_key", "None")
        expires_in = j_obj.get("expires_in", 1500)
        memcache.set(open_id, session_key, expires_in)
        return jsonify(status="success", open_id=open_id)


"""
@app.route('/auto/<app>/<ctrl>/<pk>')
def rout_handler(app, ctrl, pk):
    return 'Under Construct'
"""

if __name__ == '__main__':
    session.permanent = True
    app.secret_key = '\x14\x02\xacQ{\x17I\xbbU\xe1\xe1\xf2`\x05\x0fS\xd4\x0eC\x8d)\xa4\xe6\xb6'
    app.run(debug=True)
