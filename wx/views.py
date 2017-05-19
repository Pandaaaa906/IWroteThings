import json
import urllib2
from functools import wraps

from google.appengine.api import memcache

from flask import current_app as app, request, jsonify, Blueprint
from my_module.WXBizDataCrypt import WXBizDataCrypt
from my_module.functions import mCrypt
from wx_auth.models import User

wx_page = Blueprint('wx_page', __name__,
                    template_folder='templates')


def check_wx_referer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        referer = request.headers.get('referer', "")
        app_id = app.config.get('APP_ID', "")
        st = "https://servicewechat.com/{appid}".format(appid=app_id)
        if not referer.startswith(st):
            return "You're Not My Little App"
        return f(*args, **kwargs)

    return decorated_function


@wx_page.route('/login', methods=["GET", "POST"])
@check_wx_referer
def login():
    open_id = request.args.get("open_id")
    mAES = mCrypt()
    open_id = mAES.decrypt(open_id)
    session_key = memcache.get(open_id, None)
    if session_key is None:
        return jsonify(status="fail", msg="Session Lost Please re-Login")
    else:
        app_id = app.config.get('APP_ID', None)
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


@wx_page.route('/get_session')
# @check_wx_referer
def get_session():
    js_code = request.args.get('js_code', '')
    app_id = app.config.get('APP_ID', None)
    app_secret = app.config.get('APP_SECRET', None)
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
