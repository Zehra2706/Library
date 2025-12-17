from datetime import datetime, timedelta
from flask import g, render_template, request, jsonify, redirect, session, url_for, flash, Blueprint
from auth import  token_required
from entity.borrow_entity import Borrow
from entity.user_entity import User
from repository import borrow_repository
import jwt
from config import Config
from core.database import get_connection 
from services.user_services import (user_login, add_user, change_password ,get_all_users)
#from services.book_services import (get_books, get_book_by_id, add_book, delete_book)
#from services.borrow_services import ( request_borrow, get_pending_borrows, approve_borrow, reject_borrow,get_user_borrows, get_all_borrows, process_return)


user_bp = Blueprint('user_bp', __name__, template_folder='templates')

# --- HTML Sayfası Yönlendirmeleri ---


# --- Kullanıcı/Giriş Çıkış Rotaları ---

@user_bp.route('/')
def index():
    return render_template("index.html")

# Diğer tüm sayfa yönlendirmeleri de buraya gelir (login_page, signup_page, personel_panel vb.)

@user_bp.route('/login_page')
def login_page():
    return render_template("login.html")

@user_bp.route('/signup_page')
def signup_page():
    return render_template("signup.html")
    
@user_bp.route('/personel_panel')
@token_required
def personel_panel():
    if g.rol != "personel":
        resp = redirect(url_for('user_bp.index'))
        resp.set_cookie("token", "", expires=0, path="/")
        flash("Bu sayfayı sadece personel görebilir!", "danger")
        return resp
    return render_template('personel_panel.html')

@user_bp.route('/kullanici_panel')
@token_required
def kullanici_panel():
    if g.rol != "kullanici":
        resp = redirect(url_for('user_bp.index'))
        resp.set_cookie("token", "", expires=0, path="/")
        flash("Bu sayfayı sadece kullanıcı görebilir!", "danger")
        return resp
    return render_template('kullanici_panel.html')

@user_bp.route('/şifre_panel')
@token_required
def şifre_panel():
    return render_template('sifre_degistir.html')

# routes.py içine ekleyin (HTML Sayfası Yönlendirmeleri altına)

@user_bp.route('/user_login_page')
def user_login_page():
    # Bu rotanın HTML şablonundan çağrılması muhtemeldir
    return render_template("user_login.html")

@user_bp.route('/personel_login_page')
def personel_login_page():
    # Bu rotanın HTML şablonundan çağrılması muhtemeldir
    return render_template("personel_login.html")

@user_bp.route('/logout')
def logout():
    resp = redirect(url_for('user_bp.index'))
    resp.set_cookie("token", "", expires=0, path="/")  # Token tamamen silinir
    flash("Başarıyla çıkış yaptınız.", "info")
    return resp


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "hata": "Eksik veri"}), 400
    
    user = user_login(username, password) # İş Katmanı çağrısı
    
    if not user:
        return jsonify({"success": False, "hata": "Kullanıcı adı veya parola hatalı"}), 401

    session['user_id'] = user.id
    session['rol'] = user.rol  # veya user.role

    expiration = datetime.utcnow() + timedelta(minutes=Config.JWT_EXPIRATION_MINUTES)
    token= jwt.encode(
       {
            "user_id": user.id,
            "rol": user.rol , 
            "exp": expiration
       },
        Config.SECRET_KEY,
        algorithm="HS256"
    )
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    resp = jsonify({
        "success": True,
        "rol": user.rol,
        "isim": user.isim,
        "redirect": "/personel_panel" if user.rol == "personel" else "/kullanici_panel"
    })  
    resp.set_cookie("token", token, httponly=True, samesite='Lax', secure=True , path="/")

    print("TOKEN:", token)
    return resp

@user_bp.route('/uye', methods=['POST'])
def uye_ekle():
    data = request.get_json()
    # Veri kontrolü burada (Eksik alan kontrolü)
    success, mesaj = add_user(data['isim'], data['email'], data['parola'], data.get('rol', 'kullanici')) # İş Katmanı çağrısı
    if success:
        return jsonify({"mesaj": mesaj}), 200
    else:
        return jsonify({"hata": mesaj}), 400

@user_bp.route('/sifre_degistir', methods=['POST'])
@token_required
def sifre_degistir():
    try:
        data = request.get_json()
        success, mesaj = change_password(data.get('isim'), data.get('eskiSifre'), data.get('yeniSifre')) # İş Katmanı çağrısı
        if success:
            return jsonify({"mesaj": mesaj}), 200
        else:
            return jsonify({"hata": mesaj}), 401
    except Exception as e:
        return jsonify({"hata": "Sunucu hatası", "detay": str(e)}), 500

@user_bp.route('/api/search_users')
@token_required
def search_users():
    query = request.args.get('query', '').lower()
    all_users = get_all_users() # İş Katmanı çağrısı
    filtered_users = []

    for u in all_users:
        if query in (u.get("isim") or "").lower():
            filtered_users.append({
                "id": u.get("id"),
                "isim": u.get("isim"),
                "email": u.get("email"),
                "rol": u.get("rol"),
                "giris_tarihi": u.get("giris_tarihi") if u.get("giris_tarihi") else "-"
            })

    return jsonify(filtered_users)

@user_bp.route('/api/get_users', methods=['GET'])
@token_required
def get_users_simple():
    liste = get_all_users() # İş Katmanı çağrısı
    return jsonify(liste)

@user_bp.route('/kullanicilar')
@token_required
def kullanicilar():
    if g.rol != "personel":
        flash("Bu sayfayı sadece personel görebilir!", "danger")
        return redirect("/")

    liste = get_all_users() # İş Katmanı çağrısı
    return render_template("kullanicilar.html", kullanicilar=liste)

@user_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@token_required
def delete_user(user_id):
    if g.rol != "personel":
        flash("Bu işlemi yapmaya yetkiniz yok!", "danger")
        return redirect(url_for('user_bp.index'))

    from repository import user_repository
    user = user_repository.get_by_id(user_id)
    if not user:
        flash("Kullanıcı bulunamadı!", "danger")
        return redirect(url_for('user_bp.kullanicilar'))

    user_repository.delete(user)
    flash("Kullanıcı başarıyla silindi.", "success")
    return redirect(url_for('user_bp.kullanicilar'))

@user_bp.route('/get_borrow_id')
@token_required
def get_borrow_id():
    user_id = g.user_id
    borrow =Borrow.query.filter(user_id=user_id).filter(Borrow.ceza > 0).first()
    return {"borrow_id": borrow.id if borrow else None}

@user_bp.route("/get_user_id")
@token_required
def get_user_id():
    user_id = g.user_id
    
    if not user_id:
        return jsonify({"error": "not logged in"}), 401
    return jsonify({"user_id": user_id})



