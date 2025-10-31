from flask import Flask, jsonify, render_template, request , redirect, url_for, flash, session 
# from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(__name__)
app.secret_key = "supersecretkey123"

CORS(app)

pymysql.install_as_MySQLdb() 


# MySQL bağlantı ayarları 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Zehra123.@localhost/kutuphane'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

@app.route('/personel_panel')
def personel_panel():
    return render_template('personel_panel.html')

@app.route('/kullanici_panel')
def kullanici_panel():
    return render_template('kullanici_panel.html')

@app.route('/kitap_ekle_form')
def kitap_ekle_form():
    return render_template('kitap_ekle.html')

@app.route('/şifre_panel')
def şifre_panel():
    return render_template('sifre_degistir.html')



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    parola = db.Column(db.String(300), nullable=False)
    rol=db.Column(db.String(50),nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(150), nullable=False)
    yazar=db.Column(db.String(150),nullable=False)
    kategori_id=db.Column(db.Integer,db.ForeignKey('category.id'))
    kategori = db.relationship("Category", backref="kitaplar")
    mevcut= db.Column(db.Integer)
    image_url = db.Column(db.String(200), nullable=True)
    detay=db.Column(db.String(400), nullable=True)

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    user = db.relationship('User', backref='borrows')
    book_id=db.Column(db.Integer,db.ForeignKey('book.id'))
    alis_tarihi=db.Column(db.DateTime, default=datetime.utcnow)
    iade_tarihi=db.Column(db.DateTime)
    gercek_iade_tarihi = db.Column(db.DateTime, nullable=True)   # <-- eklendi
    ceza=db.Column(db.Float, default=0.0)
    durum=db.Column(db.String(20),default='beklemede')
    book= db.relationship('Book', backref='borrows')  

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')  # frontend’den gelen
    password = data.get('password')  # frontend’den gelen
    
    if not username or not password:
        return jsonify({"success": False, "hata": "Eksik veri"}), 400

    # Kullanıcıyı database’de isim + parola ile kontrol et
    user = User.query.filter_by(isim=username).first()
    if user and check_password_hash(user.parola , password):
        rol = user.rol
        session['rol'] = rol
        session['isim'] = user.isim
        session['user_id'] = user.id

        if rol== "personel":
            redirect_page="/personel_panel"
        elif rol == "kullanıcı":
            redirect_page="/kullanici_panel"
        else:
            redirect_page="/"        

        return jsonify({"success": True, "rol": rol, "isim":user.isim, "redirect": redirect_page}),200
    else:
        return jsonify({"success": False, "hata": "Kullanıcı adı veya parola hatalı"}), 401
    

@app.route('/uye', methods=['POST'])
def uye_ekle():
    data=request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"hata": "Bu e-posta ile zaten bir hesap var!"}), 400
    
    hashed_password= generate_password_hash(data['parola'])
    yeni=User(
        isim=data['isim'],
        email=data['email'],
        parola=hashed_password,
        rol=data.get('rol' , 'kullanıcı')
    )
    db.session.add(yeni)
    db.session.commit()
    return jsonify({"mesaj": "Üye eklendi."})

@app.route('/sifre_degistir', methods=['POST'])
def sifre_degistir():
    try:    
        data= request.get_json()
        isim=data.get('isim')
        eski=data.get('eskiSifre')
        yeni=data.get('yeniSifre')

        if not isim or not eski or not yeni:
           return jsonify({"hata": "tüm alanlar doldurulmalı."}),400

        user=User.query.filter_by(isim=isim).first()

        if not user:
           return jsonify({"hata": "mevcut sifre hatalı veya kullanıcı bulunamadı "}),401

        if not check_password_hash(user.parola, eski):
            return jsonify({"hata": "Mevcut şifre yanlış!"}), 401
       
        user.parola=generate_password_hash(yeni)
        db.session.commit()
        return jsonify({"mesaj":"Şifre başarıyla değiştirildi."}),200
    
    except Exception as e:
        return jsonify({"hata": "Sunucu hatası", "detay": str(e)}), 500     

@app.route('/kitaplar')
def kitaplar():
    q = request.args.get("q", "")
    if q:
        kitap_listesi=Book.query.filter(Book.baslik.like(f"%{q}%")).all()
    else:
        kitap_listesi=Book.query.all()

    kitaplar_json_listesi = []
    for kitap in kitap_listesi:
        kitaplar_json_listesi.append({
            'id':kitap.id,
            'baslik':kitap.baslik,
            'yazar':kitap.yazar,
            'kategori_id':kitap.kategori_id,
            'mevcut':kitap.mevcut,
            'image_url':kitap.image_url if kitap.image_url else ''
        }) 
    return render_template("kitaplar.html", kitaplar_data=kitaplar_json_listesi or [], arama=q)     

@app.route('/kitap/<int:kitap_id>')
def kitap_detay(kitap_id):
    kitap=Book.query.get_or_404(kitap_id)
    kategori_adi=kitap.kategori.isim if kitap.kategori else "Bilinmiyor"

    return render_template('kitap_detay.html' , kitap={
        'id':kitap.id,
        'baslik':kitap.baslik,
        'yazar':kitap.yazar,
        'kategori':kategori_adi,
        'detay':getattr(kitap,"detay","Açıklama yok."),
        'mevcut':kitap.mevcut,
        'image_url':kitap.image_url or ''
    },session=session)


@app.route('/kitap', methods=['POST'])
def kitap_ekle():
    data=request.get_json()
    yeni_kitap=Book(
        baslik=data["baslik"],
        yazar=data["yazar"],
        kategori_id=data["kategori_id"],
        mevcut=data["mevcut"],
        detay=data["detay"],
        image_url=data["image_url"]
    )
    db.session.add(yeni_kitap)
    db.session.commit()
    return jsonify({"mesaj": "Kitap eklendi."})

@app.route('/kitaplar_json', methods=['GET'])
def kitaplari_getir():
    arama=request.args.get('arama')
    if arama:
        kitaplar=Book.query.filter(Book.baslik.like(f"%{arama}%")).all()
    else:
        kitaplar=Book.query.all()

    liste=[]
    for k in kitaplar:
        liste.append({
            "id":k.id,
            "baslik":k.baslik,
            "yazar":k.yazar,
            "kategori_id":k.kategori_id,
            "mevcut":k.mevcut
        })     
    return jsonify(liste)  

@app.route('/kitap-form-gonder', methods=['POST'])
def kitap_form_gonder():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ["baslik" , "yazar", "kategori_id"]):
            return jsonify({"hata":"Eksik kitap bilgisi girdiniz."}),400
        
        try:
            kategori_id = int(data["kategori_id"])
        except ValueError:
            return jsonify({"hata":"Kategori ID geçerli bir sayı olmalıdır"}),400    

        yeni_kitap = Book(
            baslik=data["baslik"],
            yazar=data["yazar"],
            detay=data["detay"],
            mevcut=data["mevcut"],
            kategori_id=kategori_id,
            image_url=data.get("image_url")
        )
        db.session.add(yeni_kitap)
        db.session.commit()
        return jsonify({"mesaj":f"'{data['baslik']}' adlı kitap başarıyla eklendi"}),200
    
    except Exception as e:
        print(f"Kitap Ekleme Hatası: {e}")
        return jsonify({"hata":f"Sunucu hatası: {str(e)}"}),500


@app.route('/kitap/<int:kitap_id>',methods=['POST'])
def kitap_sil(kitap_id):
    if session.get('rol') != 'personel':
        flash("Bu işlemi yapmaya yetkiniz yok!","danger")
        return redirect(url_for('kitap_detay',kitap_id=kitap_id))

    kitap=Book.query.get_or_404(kitap_id)
    if not kitap:
        return jsonify({"hata":"Kitap bulunamadı"}),404
    db.session.delete(kitap)
    db.session.commit()
    flash(f"'{kitap.baslik}' adlı kitap silindi.", "success")
    return redirect(url_for('kitaplar'))


@app.route('/odunc', methods=['POST'])
def odunc_al():
    user_id = request.form.get('user_id')
    book_id = request.form.get('book_id')
    
    if not user_id or not book_id:
        return jsonify({"hata":"Eksik bilgi gönderildi"}),400
    
    try:
        user_id=int(user_id)
        book_id=int(book_id)
    except(TypeError,ValueError):
        return jsonify({"hata":"Geçersiz user id yada book id"}),400
 
    kitap=Book.query.get(book_id)
   
    if not kitap:
       return jsonify({"hata": "Kitap bulunamadı"}),404
   
    if kitap.mevcut is None or kitap.mevcut<= 0:
        flash("Kitap stokta yok, ödünç verilemez","danger")
        return redirect(url_for("kitap_detay", kitap_id=book_id))
   
    bugun = datetime.utcnow().date()
    bugunku_oduncler = Borrow.query.filter(
        Borrow.user_id == user_id,
        db.func.date(Borrow.alis_tarihi) == bugun,
        Borrow.durum.in_(["beklemede","onaylandı"])
    ).count()

    if bugunku_oduncler >= 3:
        flash("Aynı gün 3 den fazla kitap ödünç alamazsınız!","warning")
        return redirect(url_for("kitap_detay", kitap_id = book_id))

    ayni_gun_ayni_kitap = Borrow.query.filter(
        Borrow.user_id == user_id,
        Borrow.book_id ==book_id,
        db.func.date(Borrow.alis_tarihi) == bugun
    ).first()

    if ayni_gun_ayni_kitap:
        flash("Bu kitap için bugün zaten bir istek gönderdiniz!","danger")
        return redirect(url_for("kitap_detay", kitap_id=book_id))
    
    alis_tarihi = datetime.utcnow()
    iade_tarihi = alis_tarihi + timedelta(days=1) 
    
    odunc=Borrow(
        user_id=user_id , 
        book_id=book_id , 
        durum='beklemede',
        alis_tarihi=alis_tarihi,
        iade_tarihi=iade_tarihi
        )
    db.session.add(odunc)
    db.session.commit()
    
    flash(f"'{kitap.baslik}' kitabı için ödünç talebiniz personel onayına gönderildi.", "info")
    return redirect(url_for("kitap_detay",kitap_id=book_id))

@app.route('/bekleyen_oduncler')
def bekleyen_oduncler():
    if session.get('rol') != 'personel':
        flash("Bu sayfayı sadece personel görebilir!", "danger")
        return redirect(url_for('index'))

    bekleyenler = Borrow.query.filter_by(durum='beklemede').all()
    liste = []
    for o in bekleyenler:
        user = User.query.get(o.user_id)
        kitap = Book.query.get(o.book_id)
        liste.append({
            "id":o.id,
            "kullanici":user.isim if user else "Silinmiş",
            "kitap":kitap.baslik if kitap else "Silinmiş",
            "tarih":o.alis_tarihi.strftime("%Y-%m-%d")
    })
    return render_template("bekleyen_oduncler.html",oduncler=liste)

@app.route('/odunc_onayla/<int:odunc_id>', methods=['POST'])
def odunc_onayla(odunc_id):
    if session.get('rol') != 'personel':
        flash("Yetkiniz yok!" , "danger")
        return redirect(url_for('index'))
    
    odunc = Borrow.query.get(odunc_id)
    if not odunc:
        flash("Kayıt bulunamadı.","danger")
        return redirect(url_for('bekleyen_oduncler'))
    
    kitap = Book.query.get(odunc.book_id)
    if not kitap or kitap.mevcut<=0:
        odunc.durum='reddedildi'
        if session.get('rol') != 'kullanıcı':
            flash("Kitap stokta yok istek reddedildi","danger")

    else :
        kitap.mevcut -=1
        odunc.durum='onaylandı'
        odunc.iade_tarihi=odunc.alis_tarihi + timedelta(days=1)
        if session.get('rol') != 'kullanıcı':
            flash(f"'{kitap.baslik}' ödünç verildi. İade tarihi: {odunc.iade_tarihi.strftime('%Y-%m-%d')}", "success")

    db.session.commit()
    return redirect(url_for('bekleyen_oduncler'))

@app.route('/odunc_reddet/<int:odunc_id>' , methods=['POST'])
def odunc_reddet(odunc_id):
    if session.get('rol') != 'personel':
        flash("Yetkiniz yok!","danger")
        return redirect(url_for('index'))
    
    odunc = Borrow.query.get(odunc_id)
    if not odunc:
        flash("Kayıt bulunamadı.", "danger")
        return redirect(url_for('bekleyen_oduncler'))

    odunc.durum = 'reddedildi'
    db.session.commit()
    if session.get('rol') != 'kullanıcı':
        flash("İstek reddedildi." , "info")
    return redirect(url_for('bekleyen_oduncler'))

@app.route('/odunclerim')
def odunclerim():
    if 'isim' not in session:
        flash("Ödünç kayıtlarınızı görmek için giriş yapmalısınız.","warning")
        return redirect(url_for('login_page'))
    
    user_id = session.get("user_id")
    user = User.query.filter_by(isim=session['isim']).first()
    if not user:
        flash("Kullanıcı bulunamadı." , "danger")
        return redirect(url_for('login_page'))
    
    simdi=datetime.utcnow()
    oduncler= Borrow.query.filter_by(user_id=user_id).all()

    liste = []
    for o in oduncler:
        kitap=Book.query.get(o.book_id)
        gecikme_gun=0
        ceza = 0.0

        if o.iade_tarihi and simdi > o.iade_tarihi and o.durum == "onaylandı":
            gecikme_gun = (simdi - o.iade_tarihi).days
            ceza = gecikme_gun * 3.0
        
        
        liste.append({
            "kitap": kitap.baslik if kitap else "Silinmiş",
            "alis_tarihi":o.alis_tarihi.strftime("%Y-%m-%d"),
            "iade_tarihi":o.iade_tarihi.strftime("%Y-%m-%d") if o.iade_tarihi else "-",
            # "iade_gereken_tarih":o.iade_tarihi.strftime("%Y-%m-%d+5"),
            "gecikme_gun":gecikme_gun,
            "durum": o.durum,
            "ceza":ceza

        })    
    return render_template("odunclerim.html" , oduncler=liste)

@app.route('/tum_oduncler')
def tum_oduncler():
    if session.get('rol') != 'personel':
        flash("Bu sayfayı sadece personel görebilir!" , "danger")
        return redirect(url_for('index'))

    simdi = datetime.utcnow()
    oduncler = Borrow.query.all()

    liste = []
    for o in oduncler:
        user=User.query.get(o.user_id)
        kitap=Book.query.get(o.book_id)
        gecikme_gun=0
        ceza = o.ceza or 0.0

        if o.iade_tarihi and simdi > o.iade_tarihi and o.durum=="onaylandı":
            gecikme_gun = (simdi - o.iade_tarihi).days
            ceza = gecikme_gun * 3.0
        
        
        liste.append({
            "id":o.id,
            "kullanici": user.isim if user else "Silinmiş",
            "kitap": kitap.baslik if kitap else "Silinmiş",
            "alis_tarihi":o.alis_tarihi.strftime("%Y-%m-%d"),
            "iade_tarihi":o.iade_tarihi.strftime("%Y-%m-%d") if o.iade_tarihi else "-",
            # "iade_gereken_tarih":o.iade_tarihi.strftime("%Y-%m-%d+5"),
            "gecikme_gun":gecikme_gun,
            "durum":o.durum,
            "ceza":ceza

        })  
    # oduncler = Borrow.query.all()  
    return render_template("tum_oduncler.html" , oduncler=oduncler)

@app.route('/iade_al/<int:odunc_id>',methods=['POST'])
def iade_al(odunc_id):
    
    odunc=Borrow.query.get_or_404(odunc_id)

    if not odunc:
        flash("Kayıt bulunamadı.", "danger")
        return redirect(url_for('odunclerim'))

    if odunc.durum not in ['onaylandı']:
        flash("Bu kitap iade alınamaz, çünkü henüz onaylanmadı ya da zaten iade edildi.", "warning")
        return redirect(url_for('tum_oduncler'))
    
    odunc.durum = "iade_edildi"
    odunc.gercek_iade_tarihi = datetime.utcnow()


    if odunc.iade_tarihi and odunc.gercek_iade_tarihi.date() > odunc.iade_tarihi.date():
        gecikme = (odunc.gercek_iade_tarihi.date() - odunc.iade_tarihi.date()).days
        odunc.ceza = gecikme * 3.0
        flash(f"{odunc.user.isim} kitabı {gecikme} gün geç getirdi. Ceza: {odunc.ceza}₺", "warning")
    else: 
        flash("Kitap başarıyla iade alındı.", "success")

    kitap=Book.query.get(odunc.book_id)
    if kitap:
        kitap.mevcut = (kitap.mevcut or 0) + 1    
 
    db.session.commit()
    return redirect(url_for('tum_oduncler'))


# @app.route('/kitap/<int:id>',methods=['PUT'])
# def kitap_guncelle(id):
#     data=request.get_json()
#     kitap=book.query.get(id)
#     if not kitap:
#         return jsonify({"hata":"Kitap bulunamadı"}),404 
    
#     kitap.baslik=data.get("baslik",kitap.baslik)
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
#             "baslik":k.baslik,
#             "yazar":k.yazar,
#             "mevcut":k.mevcut
#         })
#         return jsonify(liste)

 

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
#            "kitap":kitap.baslik if kitap else "Silinmiş",
#            "alış_tarihi":odunc.alış_tarihi.strftime("%Y-%m-%d"),
#            "geçen_gün":(simdi - odunc.alış_tarihi).days 
#         })
#     return jsonify(liste)
    

if __name__ == "__main__":

    with app.app_context(): 
        # db.drop_all()
        db.create_all()
        print("Veritabanı tabloları oluşturuldu.") 
    app.run(debug=True) 

    