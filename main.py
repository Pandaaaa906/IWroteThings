from admin.views import admin_page
from auth.models import User
from flask import Flask, request, redirect
from flask import render_template, url_for
from my_module.functions import has_no_empty_params
from wx.views import wx_page

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)
app.register_blueprint(admin_page, url_prefix='/admin')
app.register_blueprint(wx_page, url_prefix='/wx')


@app.route('/')
def index():
    links = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append([url, rule.endpoint])
    print "ASDF", type(links)
    return render_template('index.html', links=links)


@app.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        name = request.form.get("name", None)
        password = request.form.get("password", None)
        return name + password


@app.route('/signup/', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        name = str(request.form.get("name", None))
        password = str(request.form.get("password", None))
        try:
            user = User.create(name=name, password=password)
        except ValueError as e:
            return e
        return redirect(url_for("login"))


if __name__ == '__main__':
    # session.permanent = True
    # app.secret_key = '\x14\x02\xacQ{\x17I\xbbU\xe1\xe1\xf2`\x05\x0fS\xd4\x0eC\x8d)\xa4\xe6\xb6'
    app.debug = True
    app.run()
