from google.appengine.ext import ndb as db


class Navbar(db.Model):
    name = db.StringProperty()
    label = db.TextProperty()
    url = db.StringProperty()

