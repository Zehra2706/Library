from flask import request
from entity.borrow_entity import Borrow
from core.database import db
from sqlalchemy import func

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

@staticmethod
def get_by_user(user_id):
        return Borrow.query.filter_by(user_id=user_id).all()

@staticmethod
def get_pending():
        return Borrow.query.filter_by(durum='beklemede').all()

@staticmethod
def has_active_same_book(user_id, book_id):
    return Borrow.query.filter(
        Borrow.user_id == user_id,
        Borrow.book_id == book_id,
        Borrow.durum.in_(["onaylandı", "beklemede"])
    ).first() is not None

@staticmethod
def count_daily_requests(user_id, bugun):
        return Borrow.query.filter(
            Borrow.user_id == user_id,
            func.date(Borrow.alis_tarihi) == bugun,
            Borrow.durum.in_(["beklemede", "onaylandı"])
        ).count()

@staticmethod 
def delete(borrow):
        db.session.delete(borrow)
        db.session.commit()

@staticmethod
def toplam_ceza(user_id):
    return db.session.query(
        func.coalesce(func.sum(Borrow.ceza), 0)
    ).filter(
        Borrow.user_id == user_id,
        Borrow.durum != "iade_edildi"
    ).scalar()# ilk satırın ilk sutununu alır.        

@staticmethod
def count_active_borrows(user_id):
    return Borrow.query.filter(
        Borrow.user_id == user_id,
        Borrow.durum == "onaylandı"
    ).count()

#Bu kod, gelen isteğin JSON mu beklediğini (API isteği mi yoksa normal web isteği mi olduğunu) kontrol eder.
@staticmethod
def wants_json_response():
    return request.is_json or request.headers.get('Accept') == 'application/json'
