from entity.email_entity import EmailQueue
from core.database import db

# class EmailRepository:

@staticmethod
def add(email):
        db.session.add(email)
        db.session.commit()
