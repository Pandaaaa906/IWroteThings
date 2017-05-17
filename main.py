import json
import urllib2

from google.appengine.api import memcache

from flask import Flask, jsonify
from flask import request
from functools import wraps
from functions.WXBizDataCrypt import WXBizDataCrypt

app = Flask(__name__)
app.config['app_id'] = "wxc2794b66adfdb911"
app.config['app_secret'] = "cbf3448395b6129dd4b08ed3b057ad7d"


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


@app.route('/wx/login')
@check_wx_referer
def login():
    app_id = app.config.get('app_id', None)
    sessionKey = 'tiihtNczf5v6AKRyjwEUhQ=='
    encryptedData = 'CiyLU1Aw2KjvrjMdj8YKliAjtP4gsMZMQmRzooG2xrDcvSnxIMXFufNstNGTyaGS9uT5geRa0W4oTOb1WT7fJlAC+oNPdbB+3hVbJSRgv+4lGOETKUQz6OYStslQ142dNCuabNPGBzlooOmB231qMM85d2/fV6ChevvXvQP8Hkue1poOFtnEtpyxVLW1zAo6/1Xx1COxFvrc2d7UL/lmHInNlxuacJXwu0fjpXfz/YqYzBIBzD6WUfTIF9GRHpOn/Hz7saL8xz+W//FRAUid1OksQaQx4CMs8LOddcQhULW4ucetDf96JcR3g0gfRK4PC7E/r7Z6xNrXd2UIeorGj5Ef7b1pJAYB6Y5anaHqZ9J6nKEBvB4DnNLIVWSgARns/8wR2SiRS7MNACwTyrGvt9ts8p12PKFdlqYTopNHR1Vf7XjfhQlVsAJdNiKdYmYVoKlaRv85IfVunYzO0IKXsyl7JCUjCpoG20f0a04COwfneQAGGwd5oa+T8yO5hzuyDb/XcxxmK01EpqOyuxINew=='
    iv = 'r7BXXKkLb8qrSNn05n0qiA=='
    return


@app.route('/wx/get_session_key')
#@check_wx_referer
def get_session_key():
    app_id = app.config.get('app_id', None)
    app_secret = app.config.get('app_secret', None)
    url = "https://api.weixin.qq.com/sns/jscode2session?appid={app_id}&secret={app_secret}&" \
          "js_code={js_code}&grant_type=authorization_code"
    js_code = request.args.get('js_code', '')
    response = urllib2.urlopen(url.format(app_id=app_id, app_secret=app_secret, js_code=js_code))
    j_obj = json.loads(response)
    open_id = j_obj.get("open_id", None)
    session_key = j_obj.get("session_key", None)
    expires_in = j_obj.get("expires_in", 1500)
    memcache.add(open_id, session_key, expires_in)
    return jsonify(status=True)


@app.route('/auto/<app>/<ctrl>/<pk>')
def rout_handler(app, ctrl, pk):
    return 'Under Construct'


if __name__ == '__main__':
    app.run()
