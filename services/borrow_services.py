from datetime import datetime, timedelta

from flask import current_app
# from werkzeug.security import generate_password_hash, check_password_hash
from entity.book_entity import Book
from core.database import db    
from entity.borrow_entity import Borrow
from entity.user_entity import User
from entity.email_entity import EmailQueue
from sqlalchemy import func

from repository import book_repository 
from repository import borrow_repository
from repository import user_repository
from repository import email_repository 

def auto_approve_old_requests():
   with current_app.app_context():
        limit_time = datetime.utcnow() - timedelta(hours=24)

        bekleyenler = Borrow.query.filter(
            Borrow.durum == "beklemede",
            Borrow.alis_tarihi <= limit_time
        ).all()

        for o in bekleyenler:
            o.durum = "onaylandı"
            # iade tarihi (senin sistemine göre)
            o.iade_tarihi = o.alis_tarihi + timedelta(minutes=1)


        if bekleyenler:
            db.session.commit()

def request_borrow(user_id, book_id):
    kitap = book_repository.get_by_id(book_id)
    if not kitap or (kitap.mevcut is None or kitap.mevcut <= 0):
        return False, "Kitap stokta yok veya bulunamadı."

    aktif_kitap_sayisi = borrow_repository.count_active_borrows(user_id)
    if aktif_kitap_sayisi >= 5:
        return False, "Üzerinizde zaten 5 kitap var. Yeni kitap alabilmek için iade yapmalısınız."
    
    bugun = datetime.utcnow().date()
    
    # Günlük limit kontrolü (Max 3 onaylanmış/beklemede ödünç)
    
    if borrow_repository.count_daily_requests(user_id, bugun) >= 3:
        return False, "Aynı gün 3' den fazla kitap alamazsınız!"

    if borrow_repository.exists_same_book_today(user_id, book_id, bugun):
        return False, "Bu kitap için bugün zaten talep gönderdiniz."

    now = datetime.utcnow()
    odunc = Borrow(
        user_id=user_id,
        book_id=book_id,
        durum='beklemede',
        alis_tarihi=None,
        iade_tarihi=None
    )

    borrow_repository.add(odunc)
    return True, f"'{kitap.baslik}' kitabı için ödünç talebiniz personel onayına gönderildi."

def get_pending_borrows():
    bekleyenler = borrow_repository.filter_by(durum='beklemede').all()
    liste = []
    for o in bekleyenler:
        user = user_repository.get_by_id(o.user_id)
        kitap = book_repository.get_by_id(o.book_id)
        liste.append({
            "id": o.id,
            "kullanici": user.isim if user else "Silinmiş",
            "kitap": kitap.baslik if kitap else "Silinmiş",
            "tarih": o.alis_tarihi.strftime("%Y-%m-%d")
        })
    return liste

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
    # Personel onayı ile gerçek iade tarihi 1 gün olarak ayarlanır (orijinal koddaki gibi)
    odunc.alis_tarihi = now
    odunc.iade_tarihi = now + timedelta(minutes=1)

    db.session.commit()

    return True, f"'{kitap.baslik}' ödünç verildi. İade tarihi: {odunc.iade_tarihi.strftime('%Y-%m-%d')}", odunc.book_id

def reject_borrow(odunc_id):
    odunc = borrow_repository.get_by_id(odunc_id)
    if not odunc:
        return False, "Ödünç kaydı bulunamadı."
    
    odunc.durum = 'reddedildi'
    borrow_repository.update()
    return True, "İstek reddedildi."

def get_user_borrows(user_id):
    simdi = datetime.utcnow()
    oduncler = borrow_repository.filter_by(user_id=user_id).all()
    liste = []
    for o in oduncler:
        kitap = Book.query.get(o.book_id)
        gecikme_gun = 0

        if o.iade_tarihi and simdi > o.iade_tarihi and o.durum == "onaylandı":
            gecikme_gun = (simdi - o.iade_tarihi).days
           # ceza = gecikme_gun * 3.0
            
        liste.append({
            "kitap": kitap.baslik if kitap else "Silinmiş",
            "alis_tarihi": o.alis_tarihi.strftime("%Y-%m-%d"),
            "iade_tarihi": o.gercek_iade_tarihi.strftime("%Y-%m-%d") if o.gercek_iade_tarihi else o.iade_tarihi.strftime("%Y-%m-%d"),
            "gecikme_gun": gecikme_gun,
            "durum": o.durum,
            "ceza": o.ceza
        })
    return liste

def get_all_borrows(user_id=None):
    db.session.expire_all()  # EVENT / TRIGGER sonrası GÜNCEL veri için

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

        gecikme_gun = 0
        if o.iade_tarihi and simdi > o.iade_tarihi and o.durum == "onaylandı":
            gecikme_gun = (simdi - o.iade_tarihi).days
        #   ceza = gecikme_gun * 3.0
            
        liste.append({
            "id": o.id,
            "user": user.isim if user else "Silinmiş",
            "kitap": kitap.baslik if kitap else "Silinmiş",
            "alis_tarihi": o.alis_tarihi.strftime("%Y-%m-%d"),
            "iade_tarihi": o.gercek_iade_tarihi.strftime("%Y-%m-%d") if o.gercek_iade_tarihi else o.iade_tarihi.strftime("%Y-%m-%d"),
            "gecikme_gun": gecikme_gun,
            "durum": o.durum,
            "ceza": o.ceza
        }) 
    return liste

def process_return(odunc_id):
    odunc = borrow_repository.get_by_id(odunc_id)
    if not odunc:
        return False, "Kayıt bulunamadı."
    if odunc.durum != 'onaylandı':
        return False, "Bu kitap iade alınamaz, çünkü henüz onaylanmadı ya da zaten iade edildi."
    
    odunc.durum = "iade_edildi"
    odunc.gercek_iade_tarihi = datetime.utcnow()
    
    ceza_mesaj = "Kitap başarıyla iade alındı."
    gecikme=0

    # if odunc.iade_tarihi and odunc.gercek_iade_tarihi.date() > odunc.iade_tarihi.date():
    #     gecikme = (odunc.gercek_iade_tarihi.date() - odunc.iade_tarihi.date()).days
    #     odunc.ceza = gecikme * 10.0
    #     ceza_mesaj = f"{odunc.user.isim} kitabı {gecikme} gün geç getirdi. Ceza: {odunc.ceza}₺"
        
    kitap = book_repository.get_by_id(odunc.book_id)
    # if kitap:
    #     kitap.mevcut = (kitap.mevcut or 0) + 1
    #     book_repository.update(kitap)


    if gecikme > 0:
        email=EmailQueue(
            user_id=odunc.user_id,
            subjectt="Gecikme Cezası Bildirimi",
            body=f"Sayın {odunc.user.isim},\n\n"
                 f'"{kitap.baslik}" kitabını {gecikme} gün geç getirdiniz.\n'
                 f"Toplam cezanız: {odunc.ceza}₺\n\n"
                 f"İyi günler dileriz."
        )    

    else:
        # Normal iade maili
        email = EmailQueue(
            user_id=odunc.user_id,
            subjectt="Kitap İade Edildi",
            body=f'Sayın {odunc.user.isim},\n\n'
                 f'"{kitap.baslik}" kitabını başarıyla iade ettiniz.\n'
                 f"İyi günler dileriz."
        )
   
    email_repository.add(email)
    return True, ceza_mesaj