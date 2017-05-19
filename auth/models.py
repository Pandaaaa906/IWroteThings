from google.appengine.ext import ndb as db
from my_module.functions import mCrypt


class User(db.Model):
    name = db.StringProperty()
    password = db.StringProperty()
    is_superuser = db.BooleanProperty(default=False)
    create_date = db.DateTimeProperty(auto_now_add=True)
    modified_date = db.DateTimeProperty(auto_now=True)

    @classmethod
    def create(cls, name, password):
        user = cls.get_by_id(name)
        if not user:
            aes = mCrypt()
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
        aes = mCrypt()
        password = aes.encrypt(password)
        user = cls.get_by_id(name)
        if user:
            if user.password == password:
                return user
            else:
                raise ValueError("Wrong Password")
        else:
            raise ValueError("User does not exist")

