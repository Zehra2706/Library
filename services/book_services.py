from sqlalchemy.exc import IntegrityError, OperationalError, DBAPIError#SQLAlchemy’den veritabanı bütünlük hatalarını yakalamak için
# from sqlalchemy.exc import IntegrityError 
from core.database import db
from repository import book_repository, category_repository, yazar_repository

def get_books(query=None):  #Tüm kitapları veya arama sonucunu döndürür
    if query:
        books = book_repository.search(query)
    else:
        books = book_repository.get_all()
    return [book.to_dict() for book in books] #SQLAlchemy objeleri JSON’a çevrilemez. Frontend / API için sade dict gerekir.

def get_book_by_id(kitap_id): # id ile kitabı alır.
    return book_repository.get_by_id(kitap_id)

def create_book(data): # Kitap oluşturur.
    print("GELEN DATA:", data)

    baslik = data.get("baslik", "").strip()
    yazar_adi = data.get("yazar", "").strip()
    kategori_adi = data.get("kategori", "").strip()
    #Gelen değerlerin varlığı kontrol edilir.
    if not baslik or not yazar_adi or not kategori_adi: 
        return False, "Başlık, yazar ve kategori zorunludur"

    yazar = yazar_repository.get_by_name(yazar_adi) # yazar adıyla o yazarı alır.
    if not yazar:
        return False, "Bu yazar sistemde kayıtlı değil"# yazarı kontrol eder.

    kategori = category_repository.get_by_name(kategori_adi)# kategori adıyla o yazarı alır.
    if not kategori:
        return False, "Kategori bulunamadı"# kategoriyi kontrol eder.

    if book_repository.exists_by_title(baslik): #Bu kitabın olup olmadıgını kontrol eder.
        return False, "Bu kitap zaten kayıtlı"

    # kitabı oluşturur.
    book_repository.create(
        baslik=baslik,
        yazar=yazar_adi,
        kategori_id=kategori.id,
        mevcut=int(data.get("mevcut", 1)),
        detay=data.get("detay"),
        image_url=data.get("image_url")
    )

    return True, "Kitap başarıyla eklendi"

#Kategori ekler.
def add_category(kategori_adi):
    from repository import category_repository
    from entity.category_entity import Category
    mevcut = category_repository.get_by_name(kategori_adi) # kategori adıyla kategoriyi alır.

    if mevcut :
        return False, "Bu isimde bir kategori zaten mevcut."    

    yeni_kategori = Category(isim=kategori_adi) # kategori adıyla kategori olusturur.
    category_repository.add(yeni_kategori) #ve ekler.
    return True, f"'{kategori_adi}' adlı kategori başarıyla eklendi"

#Yazar da kategori ile aynı şekilde eklenir.
def add_yazar(yazar_adi):
    from repository import yazar_repository
    from entity.yazar_entity import Yazar
    mevcut = yazar_repository.get_by_name(yazar_adi)

    if mevcut :
        return False, "Bu isimde bir yazar zaten mevcut."    

    yeni_yazar = Yazar(isim=yazar_adi)
    yazar_repository.add(yeni_yazar)
    return True, f"'{yazar_adi}' adlı yazar başarıyla eklendi"

#Kitap silinir.
def delete_book(kitap_id):
    kitap = book_repository.get_by_id(kitap_id)
    if not kitap:
        return False, "Kitap bulunamadı."

    try:
        book_repository.delete(kitap)
        return True, f"'{kitap.baslik}' adlı kitap silindi."

    except (OperationalError, DBAPIError) as e:
        db.session.rollback()

        hata_metni = str(e.orig) if hasattr(e, "orig") else str(e)

        # trigger mesajını yakala
        if "ödünçte" in hata_metni or "onaylandı" in hata_metni:
            return False, "Bu kitap ödünçte olduğu için silinemez."

        return False, "Veritabanı kaynaklı bir hata oluştu."

    except IntegrityError:
        db.session.rollback()
        return False, "Bu kitap silinemez (bağlı kayıtlar var)."

    except Exception as e:
        db.session.rollback()
        return False, "Silme sırasında beklenmeyen bir hata oluştu."
