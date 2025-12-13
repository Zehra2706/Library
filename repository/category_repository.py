from entity.category_entity import Category
from core.database import db

# class BookRepository:

@staticmethod
def get_all():
        return Category.query.all()

@staticmethod
def search(query):
        return Category.query.filter(Category.isim.like(f"%{query}%")).all()
@staticmethod
def get_by_id(category_isim):
        return Category.query.get(category_isim)


@staticmethod
def get_by_name(name):
        return Category.query.filter_by(isim=name).first()



@staticmethod
def add(kategori):
        db.session.add(kategori)
        db.session.commit()

@staticmethod
def delete(kategori):
    if kategori is None:
        return False, "Kategori bulunamadı"

    try:
        db.session.delete(kategori)
        db.session.commit()
        return True, " "
    except Exception as e:
        db.session.rollback()
        return False, str(e)

@staticmethod
def update(kategori):
    db.session.commit()
    return True