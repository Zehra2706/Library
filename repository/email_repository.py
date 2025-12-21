from entity.email_entity import EmailQueue
from core.database import db

@staticmethod
def add(email):
        db.session.add(email)
        db.session.commit()

@staticmethod
def get_by_id(user_id):
        return EmailQueue.query.get(user_id)

def delete_by_user_id(user_id):
    try:
        EmailQueue.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return True, "Kullanıcıya ait email kayıtları silindi."
    except Exception as e:
        db.session.rollback()
        return False, str(e)
