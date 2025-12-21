from entity.yazar_entity import Yazar
from core.database import db

@staticmethod
def get_all():
        return Yazar.query.all()

@staticmethod
def search(query):
        return Yazar.query.filter(Yazar.isim.like(f"%{query}%")).all()
@staticmethod
def get_by_id(yazar_id):
        return Yazar.query.get(yazar_id)

@staticmethod
def get_by_name(name):
        return Yazar.query.filter_by(isim=name).first()

@staticmethod
def add(yazar):
        db.session.add(yazar)
        db.session.commit()

@staticmethod
def delete(yazar):
    if yazar is None:
        return False, "Yazar bulunamadı"

    try:
        db.session.delete(yazar)
        db.session.commit()
        return True, "Yazar başarıyla silindi"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

@staticmethod
def update(yazar):
    db.session.commit()
    return True