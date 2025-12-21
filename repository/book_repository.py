from entity.book_entity import Book
from core.database import db

@staticmethod
def get_all():
        return Book.query.all()

@staticmethod
def search(query):
        return Book.query.filter(Book.baslik.like(f"%{query}%")).all()

@staticmethod
def get_by_id(book_id):
        return Book.query.get(book_id)

@staticmethod
def get_by_name(name):
        return Book.query.filter_by(isim=name).first()

#**kwargs = anahtar–değer (key=value) şeklinde sınırsız parametre alır.
@staticmethod
def create(**kwargs):
    book = Book(**kwargs)
    db.session.add(book)
    db.session.commit()        

@staticmethod
def delete(book):
        db.session.delete(book)
        db.session.commit()

@staticmethod
def update(book):
    db.session.commit()
    return True

@staticmethod
def exists_by_title(title):
    return Book.query.filter_by(baslik=title).first() is not None
