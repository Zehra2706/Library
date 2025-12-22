from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from entity.user_entity import User
from repository import user_repository
import random, string
from repository import email_repository
import send_emails
from entity.email_entity import EmailQueue
from core.database import db



#Kullanıcının giriş işlemini yapar.
def user_login(username, password):
    user = user_repository.get_by_name(username)
    if user and check_password_hash(user.parola, password):
        return user
    return None

#Kullanıcı ekler.
def add_user(isim, email, parola):
    if user_repository.get_by_email(email):
        return False, "Bu e-posta ile zaten bir hesap var!"
    
    hashed_password = generate_password_hash(parola)
    yeni = User(isim=isim, email=email, parola=hashed_password, rol="kullanici")
    user_repository.add(yeni)
    return True, "Üye başarıyla eklendi."

##Şifre değiştirir.
def change_password(isim, girilen_sifre, yeni_sifre):
    user = user_repository.get_by_name(isim)
    if not user:
        return False, "Kullanıcı bulunamadı."
    if not check_password_hash(user.parola, girilen_sifre):
        return False, "Mevcut / Geçici şifre yanlış!"
    
    user.parola = generate_password_hash(yeni_sifre)
    user.temp_password =0
    user_repository.update()
    return True, "Şifre başarıyla değiştirildi."

#Şifremi unuttum
def forgot_password(isim , email):
    user = User.query.filter_by(isim=isim, email=email).first()

    if not user:
        return False, "Kullanıcı adı ve e-posta uyuşmuyor"

    #geçici şifre üretiilir.
    temp_password = ''.join(random.choices(
        string.ascii_letters + string.digits, k=8
    ))

    user.parola =generate_password_hash(temp_password)
    user.temp_password=1 #kullanıcı geçici sifreyle giriş yapcak.
    user_repository.update()

    email_repository.add_temp_password_mail(user.id,user.email, temp_password)

    return True , "Geçici şifre e-posta ile gönderildi."

#Bütün kullanıcıları jsona uygun olarak getirir.
def get_all_users():
    return [u.to_dict() for u in user_repository.get_all()]