# from datetime import datetime, timedelta
# from werkzeug.security import generate_password_hash, check_password_hash
from entity.book_entity import Book
from core.database import db
from sqlalchemy import func

from repository import book_repository

def get_books(query=None):
    if query:
        books = book_repository.search(query)
    else:
        books = book_repository.get_all()
    return [book.to_dict() for book in books]

def get_book_by_id(kitap_id):
    return book_repository.get_by_id(kitap_id)

def add_book(baslik, yazar, kategori_id, mevcut, detay, image_url):
    try:
        kategori_id = int(kategori_id)
    except ValueError:
        return False, "Kategori ID geçerli bir sayı olmalıdır"
    
    yeni_kitap = Book(
        baslik=baslik, yazar=yazar, detay=detay,
        mevcut=mevcut, kategori_id=kategori_id, image_url=image_url
    )
    book_repository.add(yeni_kitap)
    return True, f"'{baslik}' adlı kitap başarıyla eklendi"

def delete_book(kitap_id):
    kitap = book_repository.get_by_id(kitap_id)
    if not kitap:
        return False, "Kitap bulunamadı."
    
    book_repository.delete(kitap)
    return True, f"'{kitap.baslik}' adlı kitap silindi."