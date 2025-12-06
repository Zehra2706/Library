from entity.user_entity import User
from core.database import db

# class UserRepository:

@staticmethod
def get_by_id(user_id):
        return User.query.get(user_id)

@staticmethod
def get_by_name(username):
        return User.query.filter_by(isim=username).first()

@staticmethod
def get_by_email(email):
        return User.query.filter_by(email=email).first()

@staticmethod
def add(user):
        db.session.add(user)
        db.session.commit()

@staticmethod
def update():
        db.session.commit()

@staticmethod
def get_all():
        return User.query.all()
