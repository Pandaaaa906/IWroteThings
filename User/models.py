from google.appengine.ext import ndb as db


class User(db.Model):
    unionId = db.StringProperty(unique=True)
    openId = db.StringProperty()
    nickName = db.TextProperty()
    gender = db.IntegerProperty(choices=set([0, 1, 2]))

    city = db.StringProperty()
    province = db.StringProperty()
    country = db.StringProperty()

    avatarUrl = db.StringProperty()

    join_date = db.DateTimeProperty(auto_now_add=True)
    last_login = db.DateTimeProperty(auto_now=True)