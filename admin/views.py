from importlib import import_module

from flask import render_template, Blueprint, request

admin_page = Blueprint('admin_page', __name__,
                       template_folder='templates')


@admin_page.route('/')
def index():
    return "This is a admin main page"


def iter_value(d, keys):
    for key in keys:
        yield str(getattr(d, key, ""))


@admin_page.route('/<app_label>/<model_name>/')
@admin_page.route('/<app_label>/<model_name>/<page>')
def list_view(app_label, model_name, page=1):
    per_page = 50
    models = import_module('{app}.models'.format(app=app_label))
    model = getattr(models, model_name)
    table_headers = model._properties.keys()
    results = model.query().fetch(per_page, offset=per_page * (page - 1))
    table = map(lambda x: iter_value(x, table_headers), results)
    breadcrumb = [app_label, model_name]
    return render_template("list.html",
                           breadcrumb=breadcrumb,
                           table_headers=table_headers,
                           table=table)


@admin_page.route('/<app_label>/<model_name>/add')
def add(app_label, model_name):
    if request.method == "GET":
        return render_template("add.html")