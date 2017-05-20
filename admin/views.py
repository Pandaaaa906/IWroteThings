from functools import wraps
from importlib import import_module
import inspect
from google.appengine.ext.ndb import Model as ndb_model

from flask import render_template, Blueprint, request, abort, current_app as app, g
from my_module.functions import debug_error

admin_page = Blueprint('admin_page', __name__,
                       template_folder='templates')


class AppList(object):
    def __init__(self, app_label):
        self.app_label = app_label
        self.models = set()

    def add(self, model_name):
        self.models.add(model_name)


@admin_page.route('/')
@debug_error
def index():
    installed_apps = app.config.get("INSTALLED_APPS", [])
    table = []
    for app_label in installed_apps:
        applist = AppList(app_label)
        try:
            module = import_module('{app}.models'.format(app=app_label))
        except ImportError:
            continue
        for cls_name in dir(module):
            klss = getattr(module, cls_name)
            if inspect.isclass(klss):
                if issubclass(klss, ndb_model):
                    applist.add(cls_name)
        table.append(applist)
    return render_template("/admin/index.html",
                           table=table)


def iter_value(d, keys):
    print d
    for key in keys:
        yield str(getattr(d, key, ""))


@admin_page.route('/<app_label>/<model_name>/')
@admin_page.route('/<app_label>/<model_name>/<page>')
def list_view(app_label, model_name, page=1):
    per_page = 50
    try:
        models = import_module('{app}.models'.format(app=app_label))
        model = getattr(models, model_name)
    except:
        return abort(404)
    table_headers = model._properties.keys()
    results = model.query().fetch(per_page, offset=per_page * (page - 1))
    table = map(lambda x: list(iter_value(x, table_headers)), results)
    print table
    breadcrumb = [app_label, model_name]
    return render_template("admin/list.html",
                           breadcrumb=breadcrumb,
                           table_headers=table_headers,
                           table=table)


@admin_page.route('/<app_label>/<model_name>/add')
def add(app_label, model_name):
    if request.method == "GET":
        return render_template("admin/add.html")
