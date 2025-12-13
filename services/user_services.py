#from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from entity.user_entity import User
from entity.email_entity import EmailQueue
from entity.book_entity import Book
from entity.borrow_entity import Borrow
from core.database import db
from sqlalchemy import func

from repository import user_repository

# --- Kullanıcı Hizmetleri ---

def user_login(username, password):
    user = user_repository.get_by_name(username)
    if user and check_password_hash(user.parola, password):
        return user
    return None

def add_user(isim, email, parola, rol='kullanici'):
    if user_repository.get_by_email(email):
        return False, "Bu e-posta ile zaten bir hesap var!"
    
    hashed_password = generate_password_hash(parola)
    yeni = User(isim=isim, email=email, parola=hashed_password, rol=rol)
    # db.session.add(yeni)
    # db.session.commit()
    user_repository.add(yeni)
    return True, "Üye başarıyla eklendi."

def change_password(isim, eski_sifre, yeni_sifre):
    user = user_repository.get_by_name(isim)
    if not user:
        return False, "Kullanıcı bulunamadı."
    if not check_password_hash(user.parola, eski_sifre):
        return False, "Mevcut şifre yanlış!"
    
    user.parola = generate_password_hash(yeni_sifre)
    user_repository.update()
    return True, "Şifre başarıyla değiştirildi."


def get_all_users():
    return [u.to_dict() for u in user_repository.get_all()]