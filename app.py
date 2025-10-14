from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
# from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})


pymysql.install_as_MySQLdb()



# MySQL bağlantı ayarları 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Zehra123.@localhost/kutuphane'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login_page')
def login_page():
    return render_template("login.html")

@app.route('/signup_page')
def signup_page():
    return render_template("signup.html")

@app.route('/user_login_page')
def user_login_page():
    return render_template("user_login.html")

@app.route('/personel_login_page')
def personel_login_page():
    return render_template("personel_login.html")




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    parola = db.Column(db.String(100), nullable=False)
    rol=db.Column(db.String(50),nullable=False)

class category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)

class book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    başlık = db.Column(db.String(150), nullable=False)
    yazar=db.Column(db.String(150),nullable=False)
    kategori_id=db.Column(db.Integer,db.ForeignKey('category.id'))
    mevcut= db.Column(db.Boolean, default=True)

class borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    book_id=db.Column(db.Integer,db.ForeignKey('book.id'))
    alış_tarihi=db.Column(db.DateTime, default=datetime.utcnow)
    iade_tarihi=db.Column(db.DateTime)    
    ceza=db.Column(db.Float, default=0.0)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')  # frontend’den gelen
    password = data.get('password')  # frontend’den gelen
    
    if not username or not password:
        return jsonify({"success": False, "hata": "Eksik veri"}), 400

    # Kullanıcıyı database’de isim + parola ile kontrol et
    user = User.query.filter_by(isim=username, parola=password).first()

    if user:
        rol = user.rol

        if rol== "personel":
            redirect_page="personel_panel.html"
        elif rol == "kullanıcı":
            redirect_page="kullanici_panel.html"
        else:
            redirect_page="index.html"        

        return jsonify({"success": True, "rol": rol, "isim":user.isim, "redirect": redirect_page}),200
    else:
        return jsonify({"success": False, "hata": "Kullanıcı adı veya parola hatalı"}), 401
    

@app.route('/uye', methods=['POST'])
def uye_ekle():
    data=request.get_json()
    yeni=User(
        isim=data['isim'],
        email=data['email'],
        parola=data['parola'],
        rol=data['rol']
    )
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"hata": "Bu e-posta ile zaten bir hesap var!"}), 400
    db.session.add(yeni)
    db.session.commit()
    return jsonify({"mesaj": "Üye eklendi."})

    

@app.route('/personel_panel')
def personel_panel():
    return render_template('personel_panel.html')

@app.route('/kullanici_panel')
def kullanici_panel():
    return render_template('kullanici_panel.html')

@app.route('/sifre_degistir', methods=['POST'])
def sifre_degistir():
    try:    
        data= request.get_json()
        isim=data.get('isim')
        eski=data.get('eskiSifre')
        yeni=data.get('yeniSifre')

        if not isim or not eski or not yeni:
           return jsonify({"hata": "tüm alanlar doldurulmalı."}),400

        user=User.query.filter_by(isim=isim , parola=eski).first()

        if not user:
           return jsonify({"hata": "mevcut sifre hatalı veya kullanıcı bulunamadı "}),401

        if user.parola != eski:
           return jsonify({"hata": "Mevcut şifre yanlış!"}), 401
    
        user.parola=yeni
        db.session.commit()
        return jsonify({"mesaj":"Şifre başarıyla değiştirildi."}),200
    
    except Exception as e:
        return jsonify({"hata": "Sunucu hatası", "detay": str(e)}), 500     



# @app.route('/kitap', methods=['POST'])
# def kitap_ekle():
#     data=request.get_json()
#     yeni_kitap=book(
#         başlık=data["başlık"],
#         yazar=data["yazar"],
#         kategori_id=data["kategori_id"],
#         # mevcut=data["mevcut"]
#     )
#     db.session.add(yeni_kitap)
#     db.session.commit()
#     return jsonify({"mesaj": "Kitap eklendi."})

# @app.route('/odunc', methods=['POST'])
# def odunc_ver():
#     data=request.get_json()
#     kitap=book.query.get(data['book_id'])
#     if not kitap.mevcut:
#        return jsonify({"hata": "Kitap zaten ödünçte"}),400
#     kitap.mevcut=False
#     odunc=borrow(user_id=data['user_id'],book_id=data['book_id'])
#     db.session.add(odunc)
#     db.session.commit()
#     return jsonify({"mesaj":" Kitap ödünç verildi."})


# @app.route('/iade/<int:barrow_id>',methods=['PUT'])
# def kitap_iade(barrow_id):
#     odunc=borrow.query.get(barrow_id)
#     if not odunc:
#         return jsonify({"hata":"Kayıt Bulunamadı"})
    
#     odunc.iade_tarihi=datetime.utcnow()

#     # ceza 7 günden fazla geçerse her gün iki tl
#     fark=(odunc.iade_tarihi - odunc.alış_tarihi).days
#     if fark>7:
#         odunc.ceza = (fark - 7)*2.0

#     kitap=book.query.get(odunc.book_id)
#     kitap.mevcut=True

#     db.session.commit()
#     return jsonify({"mesaj":"Kitap iade alındı", " ceza ":odunc.ceza})    



# @app.route('/kitap/<int:id>',methods=['DELETE'])
# def kitap_sil(id):
#     kitap=book.query.get(id)
#     if not kitap:
#         return jsonify({"hata":"Kitap bulunamadı"}),404
#     db.session.delete(kitap)
#     db.session.commit()
#     return jsonify({"mesaj":"Kitap silindi."})


# @app.route('/kitap/<int:id>',methods=['PUT'])
# def kitap_guncelle(id):
#     data=request.get_json()
#     kitap=book.query.get(id)
#     if not kitap:
#         return jsonify({"hata":"Kitap bulunamadı"}),404
    
#     kitap.başlık=data.get("başlık",kitap.başlık)
#     kitap.yazar=data.get("yazar",kitap.yazar)
#     kitap.kategori_id=data.get("kategori_id",kitap.kategori_id)
#     db.session.commit()

#     return jsonify({"mesaj":"Kitap güncellendi."})
    
# @app.route('/kategori', methods=['POST'])    
# def kategori_ekle():
#     data=request.get_json()
#     yeni=category(isim=data['isim'])
#     db.session.add(yeni)
#     db.session.commit()
#     return jsonify({"mesaj":"Kategori eklendi."})

# @app.route('/kategoriler', methods=['GET'])
# def kategorileri_getir():
#     kategoriler= category.query.all()
#     liste=[]
#     for kat in kategoriler:
#         liste.append({
#             "id":kat.id,
#             "isim":kat.isim
#         })
#     return jsonify(liste)

# @app.route('/kategori/<int:kategori_id>/kitaplar',methods=['GET'])
# def kategori_kitaplari(kategori_id):
#     kitaplar = book.query.filter_by(kategori_id=kategori_id).all()
#     liste = []
#     for k in kitaplar:
#         liste.append({
#             "id":k.id,
#             "başlık":k.başlık,
#             "yazar":k.yazar,
#             "mevcut":k.mevcut
#         })
#         return jsonify(liste)

# @app.route('/kitaplar', methods=['GET'])
# def kitaplari_getir():
#     arama=request.args.get('arama')
#     if arama:
#         kitaplar=book.query.filter(book.başlık.like(f"%{arama}%")).all()
#     else:
#         kitaplar=book.query.all()

#     liste=[]
#     for k in kitaplar:
#         liste.append({
#             "id":k.id,
#             "başlık":k.başlık,
#             "yazar":k.yazar,
#             "kategori_id":k.kategori_id,
#             "mevcut":k.mevcut
#         })     
#     return jsonify(liste)  

# @app.route('/gecikenler',methods=['GET'])
# def geciken_kitaplar():
#     simdi=datetime.utcnow()
#     gecikenler=borrow.query.filter(
#         borrow.iade_tarihi.is_(None),
#         (simdi - borrow.alış_tarihi).days > 7
#     ).all()
    
#     liste=[]
#     for odunc in gecikenler:
#         kullanici=User.query.get(odunc.user_id)
#         kitap = book.query.get(odunc.book_id)
#         liste.append({
#            "ödünç_id":odunc.id,
#            "kullanıcı":kullanici.isim if kullanici else "Bilinmiyor",
#            "kitap":kitap.başlık if kitap else "Silinmiş",
#            "alış_tarihi":odunc.alış_tarihi.strftime("%Y-%m-%d"),
#            "geçen_gün":(simdi - odunc.alış_tarihi).days 
#         })
#     return jsonify(liste)
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Veritabanı tabloları oluşturuldu.")
       
    app.run(debug=True) 

    