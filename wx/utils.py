import traceback
from functools import wraps

import sys

from flask.json import jsonify
from flask import request,current_app as app


class JsonResponse(dict):
    def __init__(self, **kwargs):
        self.setdefault('status', 'success')
        for k, v in kwargs.items():
            self[k] = v

    @property
    def status(self):
        return self.get('status')

    @status.setter
    def status(self, value):
        if value in ("success", "fail"):
            self['status'] = value


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


def wx_debug(f):
    @wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseException as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            j_obj = JsonResponse(status="fail", msg=msg)
            print e

            return jsonify(j_obj)
    return func
