# from datetime import datetime, timedelta
# from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from entity.book_entity import Book
from core.database import db
from sqlalchemy import func

from entity.category_entity import Category
from repository import book_repository, category_repository, category_repository

def get_books(query=None):
    if query:
        books = book_repository.search(query)
    else:
        books = book_repository.get_all()
    return [book.to_dict() for book in books]

def get_book_by_id(kitap_id):
    return book_repository.get_by_id(kitap_id)

def add_book(baslik, yazar_adi, kategori_id, mevcut, detay, image_url):
    try:
        kategori = category_repository.get_by_id(kategori_id)    
    except ValueError:
        return False, "Kategori geçerli olmalıdır"
    
    yeni_kitap = Book(
        baslik=baslik, yazar=yazar_adi, detay=detay,
        mevcut=mevcut,kategori_id=kategori_id,
        image_url=image_url
    )
    book_repository.add(yeni_kitap)
    return True, f"'{baslik}' adlı kitap başarıyla eklendi"

def add_category(kategori_adi):
    from repository import category_repository
    from entity.category_entity import Category
    mevcut = category_repository.get_by_name(kategori_adi)

    if mevcut :
        return False, "Bu isimde bir kategori zaten mevcut."    

    yeni_kategori = Category(isim=kategori_adi)
    category_repository.add(yeni_kategori)
    return True, f"'{kategori_adi}' adlı kategori başarıyla eklendi"

def add_yazar(yazar_adi):
    from repository import yazar_repository
    from entity.yazar_entity import Yazar
    mevcut = yazar_repository.get_by_name(yazar_adi)

    if mevcut :
        return False, "Bu isimde bir yazar zaten mevcut."    

    yeni_yazar = Yazar(isim=yazar_adi)
    yazar_repository.add(yeni_yazar)
    return True, f"'{yazar_adi}' adlı yazar başarıyla eklendi"

def delete_book(kitap_id):
    kitap = book_repository.get_by_id(kitap_id)
    if not kitap:
        return False, "Kitap bulunamadı."

    try:
        book_repository.delete(kitap)
        return True, f"'{kitap.baslik}' adlı kitap silindi."
    except IntegrityError:
        db.session.rollback()
        return False, "Bu kitap ödünçte olduğu için silinemez"
    except Exception as e:
        db.session.rollback()
        return False, "Silme sırasında hata oluştu"        

 