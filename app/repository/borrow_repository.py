from entity.borrow_entity import Borrow
from core.database import db
from sqlalchemy import func

# class BorrowRepository:
@staticmethod
def all():
    return Borrow.query.all()

@staticmethod
def add(borrow):
        db.session.add(borrow)
        db.session.commit()

@staticmethod
def update():
        db.session.commit()

@staticmethod
def get_by_id(odunc_id):
        return Borrow.query.get(odunc_id)

@staticmethod
def filter_by(**kwargs):
        return Borrow.query.filter_by(**kwargs)
# def get_all():
#         return Borrow.query.all()

@staticmethod
def get_by_user(user_id):
        return Borrow.query.filter_by(user_id=user_id).all()

@staticmethod
def get_pending():
        return Borrow.query.filter_by(durum='beklemede').all()

@staticmethod
def count_daily_requests(user_id, bugun):
        return Borrow.query.filter(
            Borrow.user_id == user_id,
            func.date(Borrow.alis_tarihi) == bugun,
            Borrow.durum.in_(["beklemede", "onaylandı"])
        ).count()

@staticmethod
def exists_same_book_today(user_id, book_id, bugun):
        return Borrow.query.filter(
            Borrow.user_id == user_id,
            Borrow.book_id == book_id,
            func.date(Borrow.alis_tarihi) == bugun,
        ).first()

@staticmethod
def delete(borrow):
        db.session.delete(borrow)
        db.session.commit()
