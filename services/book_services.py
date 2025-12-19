# from datetime import datetime, timedelta
# from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from entity.book_entity import Book
from core.database import db
from sqlalchemy import func

from entity.category_entity import Category
from repository import book_repository, category_repository, yazar_repository

def get_books(query=None):
    if query:
        books = book_repository.search(query)
    else:
        books = book_repository.get_all()
    return [book.to_dict() for book in books]

def get_book_by_id(kitap_id):
    return book_repository.get_by_id(kitap_id)

def create_book(data):
    print("GELEN DATA:", data)

    # ✅ DEĞİŞKENLER EN BAŞTA TANIMLI
    baslik = data.get("baslik", "").strip()
    yazar_adi = data.get("yazar", "").strip()
    kategori_adi = data.get("kategori", "").strip()

    if not baslik or not yazar_adi or not kategori_adi:
        return False, "Başlık, yazar ve kategori zorunludur"

    # ✅ YAZAR KONTROLÜ
    yazar = yazar_repository.get_by_name(yazar_adi)
    if not yazar:
        return False, "Bu yazar sistemde kayıtlı değil"

    # ✅ KATEGORİ KONTROLÜ
    kategori = category_repository.get_by_name(kategori_adi)
    if not kategori:
        return False, "Kategori bulunamadı"

    # ✅ AYNI KİTAP KONTROLÜ
    if book_repository.exists_by_title(baslik):
        return False, "Bu kitap zaten kayıtlı"

    # ✅ KAYIT
    book_repository.create(
        baslik=baslik,
        yazar=yazar_adi,
        kategori_id=kategori.id,
        mevcut=int(data.get("mevcut", 1)),
        detay=data.get("detay"),
        image_url=data.get("image_url")
    )

    return True, "Kitap başarıyla eklendi"

# def create_book(data):
#     print("GELEN DATA:", data)

#     baslik = data.get("baslik").strip()
#     yazar = data.get("yazar").strip()
#     kategori_adi = data.get("kategori") or data.get("kategori_id").strip()

#     if not baslik or not yazar or not kategori_adi:
#         return False, "Baslik, yazar ve kategori zorunludur"

#     yazar = yazar_repository.get_by_name(yazar_adi)
#     if not yazar:
#         return False, "Bu yazar sistemde kayıtlı değil"

#     yazar_adi = yazar.strip()
#     if not yazar_adi:
#         return False, "Yazar adı boş olamaz"

#     kategori = category_repository.get_by_name(kategori_adi)
#     if not kategori:
#         return False, "Kategori bulunamadı"

#     if book_repository.exists_by_title(baslik):
#         return False, "Bu kitap zaten kayıtlı"

#     book_repository.create(
#         baslik=baslik.strip(),
#         yazar=yazar.adi,
#         kategori_id=kategori.id,
#         mevcut=int(data.get("mevcut", 1)),
#         detay=data.get("detay"),
#         image_url=data.get("image_url")
#     )

#     return True, "Kitap başarıyla eklendi"


# def create_book(data):
#     print("GELEN DATA:", data)
#     # Validation
#     required_fields = ["baslik", "yazar", "kategori"]
#     missing = [f for f in required_fields if not data.get(f)]

#     if missing:
#         return False, f"Eksik alanlar: {', '.join(missing)}"

#     yazar_adi = data["yazar"].strip()
#     if not yazar_adi:
#         return False, "Yazar adı boş olamaz"

#     # Yazar kontrolü
#     # yazar = yazar_repository.get_by_name(data["yazar"])
#     # if not yazar:
#     #     return False, "Yazar bulunamadı"

#     # Kategori kontrolü
#     kategori = category_repository.get_by_name(data["kategori"])
#     if not kategori:
#         return False, "Kategori bulunamadı"

#     # İş kuralı
#     if book_repository.exists_by_title(data["baslik"]):
#         return False, "Bu kitap zaten kayıtlı"

#     # Kaydet
#     book_repository.create(
#         baslik=data["baslik"],
#         yazar=yazar_adi,
#         kategori_id=kategori.id,
#         mevcut=data.get("mevcut", 1),
#         detay=data.get("detay"),
#         image_url=data.get("image_url")
#     )
#     return True, "Kitap başarıyla eklendi"



# def add_book(baslik, yazar_adi, kategori_id, mevcut, detay, image_url):
#     try:
#         kategori = category_repository.get_by_id(kategori_id)    
#     except ValueError:
#         return False, "Kategori geçerli olmalıdır"
    
#     yeni_kitap = Book(
#         baslik=baslik, yazar=yazar_adi, detay=detay,
#         mevcut=mevcut,kategori_id=kategori_id,
#         image_url=image_url
#     )
#     book_repository.add(yeni_kitap)
#     return True, f"'{baslik}' adlı kitap başarıyla eklendi"

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

 