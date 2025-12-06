from entity.book_entity import Book
from core.database import db

# class BookRepository:

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
def add(book):
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
