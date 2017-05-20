from flask_login import login_user, logout_user
from google.appengine.ext import ndb as db
from my_module.functions import mCrypt
from flask import current_app as app, session, g


class BlogUser(db.Model):
    name = db.StringProperty()
    password = db.StringProperty()
    is_superuser = db.BooleanProperty(default=False)
    create_date = db.DateTimeProperty(auto_now_add=True)
    modified_date = db.DateTimeProperty(auto_now=True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.key.string_id())  # python 2
        except NameError:
            return str(self.key.string_id())  # python 3

    @classmethod
    def create(cls, name, password):
        user = cls.get_by_id(name)
        if not user:
            aes = mCrypt(app.config['MKEY'], app.config['MIV'])
            password = aes.encrypt(password)
            try:
                user = cls(id=name, name=name, password=password)
            except BaseException as e:
                print e
            user.put()
            return user
        else:
            raise ValueError("Name existed")

    @classmethod
    def login(cls, name, password):
        aes = mCrypt(app.config['MKEY'], app.config['MIV'])
        password = aes.encrypt(password)
        user = cls.get_by_id(name)
        if user:
            if user.password == password:
                session["SSID"] = name
                login_user(user)
                return user
            else:
                raise ValueError("Wrong Password")
        else:
            raise ValueError("User does not exist")