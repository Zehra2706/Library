from datetime import datetime, timedelta
from entity.book_entity import Book
from core.database import db    
from entity.borrow_entity import Borrow
from repository import book_repository 
from repository import borrow_repository
from repository import user_repository

#24 saatten uzun süredir bekleyen ödünç taleplerini otomatik onaylamak için kullanılır.
def auto_approve_old_requests(app):
    # db de işlem yapmak için kullanılır.
    with app.app_context():
        print("AUTO APPROVE JOB ÇALIŞTI:", datetime.now())

        limit_time = datetime.now() - timedelta(hours=24)

        bekleyenler = Borrow.query.filter(
            Borrow.durum == "beklemede",
            Borrow.alis_tarihi <= limit_time
        ).all()
        print("Bulunan bekleyen kayıt sayısı:", len(bekleyenler))

        for o in bekleyenler:
            o.durum = "onaylandı"
            o.iade_tarihi = o.alis_tarihi + timedelta(minutes=1)

        if bekleyenler:
            db.session.commit() # eger kayıt varsa db'ye yaz.

#Kullanıcının kitap ödünç talebi oluşturması için kullanılır.
def request_borrow(user_id, book_id):
    kitap = book_repository.get_by_id(book_id)
    if not kitap or (kitap.mevcut is None or kitap.mevcut <= 0):
        return False, "Kitap stokta yok veya bulunamadı."
    #kitabın elinde olup olmadıgının kontrolunu yapar.
    if borrow_repository.has_active_same_book(user_id, book_id):
        return False, "Bu kitap zaten üzerinizde veya bekleyen bir talebiniz var."
    #Eline 5 den fazla kitap almamasını kontrol eder.
    aktif_kitap_sayisi = borrow_repository.count_active_borrows(user_id)
    if aktif_kitap_sayisi >= 5:
        return False, "Üzerinizde zaten 5 kitap var. Yeni kitap alabilmek için iade yapmalısınız."
    
    bugun = datetime.utcnow().date()
    # Gün içinde 3 den fazla kitap alınamaz.   
    if borrow_repository.count_daily_requests(user_id, bugun) >= 3:
        return False, "Aynı gün 3' den fazla kitap alamazsınız!"

    #Ödünç oluşturulur.
    odunc = Borrow(
        user_id=user_id,
        book_id=book_id,
        durum='beklemede',
        alis_tarihi=datetime.utcnow(),
        iade_tarihi=None
    )

    borrow_repository.add(odunc) # odunc db ye eklenir.
    return True, f"'{kitap.baslik}' kitabı için ödünç talebiniz personel onayına gönderildi."

#Personelin göreceği bekleyen talepler
def get_pending_borrows():
    bekleyenler = borrow_repository.filter_by(durum='beklemede').all()
    liste = []
    for o in bekleyenler:
        user = user_repository.get_by_id(o.user_id)
        kitap = book_repository.get_by_id(o.book_id)
        # Bekleyenleri listeye ekler.
        liste.append({
            "id": o.id,
            "kullanici": user.isim if user else "Silinmiş",
            "kitap": kitap.baslik if kitap else "Silinmiş",
            "tarih": o.alis_tarihi.strftime("%Y-%m-%d")
        })
    return liste

#Personel onaylar.
def approve_borrow(odunc_id):
    odunc = borrow_repository.get_by_id(odunc_id)
    if not odunc:
        return False, "Ödünç kaydı bulunamadı.", None
    
    kitap = book_repository.get_by_id(odunc.book_id)
    if not kitap or kitap.mevcut <= 0:
        odunc.durum = 'reddedildi'
        borrow_repository.update()
        return False, "Kitap stokta yok, istek reddedildi.", None

    now = datetime.utcnow()
    odunc.durum = 'onaylandı'
    # Personel onayı ile gerçek iade tarihi 1 gün olarak ayarlanır.
    odunc.alis_tarihi = now
    odunc.iade_tarihi = now + timedelta(minutes=1)

    db.session.commit()

    return True, f"'{kitap.baslik}' ödünç verildi. İade tarihi: {odunc.iade_tarihi.strftime('%Y-%m-%d')}", odunc.book_id

#Personel reddeder.
def reject_borrow(odunc_id):
    odunc = borrow_repository.get_by_id(odunc_id)
    if not odunc:
        return False, "Ödünç kaydı bulunamadı."
    
    odunc.durum = 'reddedildi'
    borrow_repository.update()
    return True, "İstek reddedildi."

#Kullanıcı kendi ödünçlerini görür.
def get_user_borrows(user_id):
    simdi = datetime.utcnow()
    oduncler = borrow_repository.filter_by(user_id=user_id).all()
    liste = []
    for o in oduncler:
        kitap = Book.query.get(o.book_id)
        liste.append({
            "kitap": kitap.baslik if kitap else "Silinmiş",
            "alis_tarihi": o.alis_tarihi.strftime("%Y-%m-%d"),
            "iade_tarihi": (
                    o.gercek_iade_tarihi.strftime("%Y-%m-%d")
                    if o.gercek_iade_tarihi
                    else o.iade_tarihi.strftime("%Y-%m-%d")
                    if o.iade_tarihi
                    else "-"
                    ),            
            "gecikme_gun": o.gecikme_gun,
            "durum": o.durum,
            "ceza": o.ceza
        })
    return liste

#personel için tüm kayıtlar
def get_all_borrows(user_id=None):
    db.session.expire_all()  # EVENT / TRIGGER sonrası güncel veri için kullanılır.

    simdi = datetime.utcnow()
    if user_id:
        oduncler = borrow_repository.filter_by(user_id=user_id).all()
    else:
        oduncler = borrow_repository.all() 
    liste = []
    for o in oduncler:
        user = user_repository.get_by_id(o.user_id)
        if not o.book_id:
            continue 
        kitap = book_repository.get_by_id(o.book_id)
            
        liste.append({
            "id": o.id,
            "user": user.isim if user else "Silinmiş",
            "kitap": kitap.baslik if kitap else "Silinmiş",
            "alis_tarihi": o.alis_tarihi.strftime("%Y-%m-%d"),
            "iade_tarihi": (
                    o.gercek_iade_tarihi.strftime("%Y-%m-%d")
                    if o.gercek_iade_tarihi
                    else o.iade_tarihi.strftime("%Y-%m-%d")
                    if o.iade_tarihi
                    else "-"
                    ),
            "gecikme_gun": o.gecikme_gun,
            "durum": o.durum,
            "ceza": o.ceza
        }) 
    return liste

#Kitap iade işlemi
def process_return(odunc_id):
    odunc = borrow_repository.get_by_id(odunc_id)
    if not odunc:
        return False, "Kayıt bulunamadı."
    if odunc.durum != 'onaylandı':
        return False, "Bu kitap iade alınamaz, çünkü henüz onaylanmadı ya da zaten iade edildi."
    
    odunc.durum = "iade_edildi"
    odunc.gercek_iade_tarihi = datetime.utcnow()
    db.session.commit()
    return True, "Kitap başarıyla iade alındı."

#Kullanıcının kitap alma fonksiyonu
def borrow_book(user_id: int, book_id: int):
    # ID kontrolü
    try:
        user_id = int(user_id)
        book_id = int(book_id)
    except (TypeError, ValueError):
        return False, "Geçersiz kullanıcı veya kitap ID"

    # Ceza kontrolü
    toplam = borrow_repository.toplam_ceza(user_id)
    if toplam >= 100:
        return False, f"Toplam cezanız {toplam} TL olduğu için yeni kitap ödünç alamazsınız."

    # Ödünç işlemi
    success, mesaj = request_borrow(user_id, book_id)
    return success, mesaj
