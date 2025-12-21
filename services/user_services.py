from werkzeug.security import generate_password_hash, check_password_hash
from entity.user_entity import User
from repository import user_repository

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
def change_password(isim, eski_sifre, yeni_sifre):
    user = user_repository.get_by_name(isim)
    if not user:
        return False, "Kullanıcı bulunamadı."
    if not check_password_hash(user.parola, eski_sifre):
        return False, "Mevcut şifre yanlış!"
    
    user.parola = generate_password_hash(yeni_sifre)
    user_repository.update()
    return True, "Şifre başarıyla değiştirildi."

#Bütün kullanıcıları jsona uygun olarak getirir.
def get_all_users():
    return [u.to_dict() for u in user_repository.get_all()]