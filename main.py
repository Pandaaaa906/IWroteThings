from admin.views import admin_page
from auth.models import BlogUser
from flask import Flask, request, redirect, g
from flask import render_template, url_for
from my_module.functions import has_no_empty_params, debug_error
from wx.views import wx_page
from flask_login import LoginManager, current_user, logout_user

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

app.register_blueprint(admin_page, url_prefix='/admin')
app.register_blueprint(wx_page, url_prefix='/wx')


@app.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(id):
    return BlogUser.get_by_id(id)


@app.route('/')
@debug_error
def index():
    links = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append([url, rule.endpoint])
    return render_template('index.html', links=links)


@app.route('/login/', methods=["GET", "POST"])
@debug_error
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        user = BlogUser.login(username=username, password=password)

        return redirect(url_for('index'))


@app.route('/logout/', methods=["GET", "POST"])
@debug_error
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/signup/', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        username = str(request.form.get("username", None))
        password = str(request.form.get("password", None))
        try:
            # import pdb;
            # pdb.set_trace();
            user = BlogUser.create(username=username, password=password)

        except ValueError as e:
            return e
        return redirect(url_for("login"))


if __name__ == '__main__':
    # session.permanent = True
    # app.secret_key = '\x14\x02\xacQ{\x17I\xbbU\xe1\xe1\xf2`\x05\x0fS\xd4\x0eC\x8d)\xa4\xe6\xb6'
    app.debug = True
    app.run()
