from google.appengine.ext import ndb as db


class User(db.Model):
    openId = db.StringProperty()
    unionId = db.StringProperty()
    nickName = db.TextProperty()
    gender = db.IntegerProperty(choices=set([0, 1, 2]))

    country = db.StringProperty()
    province = db.StringProperty()
    city = db.StringProperty()

    language = db.StringProperty()

    avatarUrl = db.StringProperty()

    join_date = db.DateTimeProperty(auto_now_add=True)
    last_login = db.DateTimeProperty(auto_now=True)
