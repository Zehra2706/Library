from flask import g, render_template, request, jsonify, redirect, url_for, flash, session, Blueprint
#from services.user_services import (user_login, add_user, change_password ,get_all_users)
from auth import token_required
from auth import token_required
from entity.category_entity import Category
from repository import category_repository
from repository.category_repository import get_all
from services.book_services import (add_category, get_books, get_book_by_id, add_book, delete_book)
#from services.borrow_services import ( request_borrow, get_pending_borrows, approve_borrow, reject_borrow,get_user_borrows, get_all_borrows, process_return)


book_bp = Blueprint('book_bp', __name__, template_folder='templates')

# @book_bp.route('/kitap_ekle_form')
# def kitap_ekle_form():
#     return render_template('kitap_ekle.html')

@book_bp.route('/kategori_ekle_form')
@token_required
def kategori_ekle_form():
    return render_template('kategori_ekle.html')

@book_bp.route('/kitaplar')
@token_required
def kitaplar():
    q = request.args.get("q", "")
    kitaplar_json_listesi = get_books(q) # İş Katmanı çağrısı
   # return redirect(url_for('book_bp.kitaplar')) 
   #print(kitaplar_json_listesi)
    return render_template("kitaplar.html", kitaplar_data=kitaplar_json_listesi, arama=q)

@book_bp.route('/kitap/<int:kitap_id>')
@token_required
def kitap_detay(kitap_id):
    kitap_obj = get_book_by_id(kitap_id)
    if not kitap_obj:
        # get_or_404 kullanımı kaldırıldı, elle 404 döndürme veya redirect
        flash("Kitap bulunamadı.", "danger")
        return redirect(url_for('book_bp.kitaplar')) 
        
    return render_template('kitap_detay.html', kitap=kitap_obj.to_dict(), session=session)

@book_bp.route('/kitap_ekle_form', methods=['GET'])
@token_required
def kitap_ekle_form():
    kategoriler = get_all()
    print(kategoriler)
    return render_template("kitap_ekle.html", kategoriler=kategoriler)


@book_bp.route('/kitap-form-gonder', methods=['POST'])
@token_required
def kitap_form_gonder():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"hata": "JSON verisi gönderilmedi."}), 400

        required_fields = ["baslik", "yazar", "kategori_id"]
        missing_fields = [f for f in required_fields if f not in data or data[f] == ""]

        # if not kategori:
        #     return jsonify({"hata": "Bu kategori bulunamadı"}), 400
        
        if missing_fields:
            return jsonify({"hata": f"Eksik alanlar: {', '.join(missing_fields)}"}), 400

        # Mevcut ve detay boş gelebilir, varsayılan değerler atanır.
        baslik = data["baslik"]
        yazar = data["yazar"]
        kategori_isim = data["kategori_id"]  # isim geliyor!
        mevcut = data.get("mevcut", 0)
        detay = data.get("detay")
        image_url = data.get("image_url")
 # İş Katmanı çağrısı

        print("gelen json: ",data)

        kategori = category_repository.get_by_name(kategori_isim)
        
        if kategori is None:
            return jsonify({"hata": "kategori bulunamadı"}), 400
        kategori_id = kategori.id

        print("kategori id: ",kategori_id)

        success, mesaj = add_book(baslik, yazar, kategori_id, mevcut, detay, image_url)
        if success:
            return jsonify({"mesaj": mesaj}), 200
        else:
            return jsonify({"hata": mesaj}), 400
    except Exception as e:
        return jsonify({"hata": f"Sunucu hatası: {str(e)}"}), 500
    

@book_bp.route('/kategori-form-gonder', methods=['POST'])
@token_required
def kategori_form_gonder():
    try:
        data = request.get_json()

        if not data or "kategori_isim" not in data:
            return jsonify({"hata": "Kategori ismi boş olamaz"}), 400

        kategori_adi = data["kategori_isim"]
        yeni = Category(isim=kategori_adi)


        if kategori_adi == "":
            return jsonify({"hata": "Kategori ismi boş olamaz"}), 400

        success, mesaj = add_category(kategori_adi)

        if success:
            return jsonify({"mesaj": mesaj}), 200
        else:
            return jsonify({"hata": mesaj}), 400

    except Exception as e:
        return jsonify({"hata": f"Sunucu hatası: {str(e)}"}), 500   

@book_bp.route('/kitap/sil/<int:kitap_id>' , methods=['POST'])
@token_required
def kitap_sil_html(kitap_id):
    if g.rol != "personel":
        flash("Bu işlemi yapmaya yetkiniz yok!", "danger")
        return redirect(url_for('book_bp.kitaplar'))

    success, mesaj = delete_book(kitap_id) # İş Katmanı çağrısı
    if success:
        flash(mesaj, "success")
    else:
        flash(mesaj, "danger")
        
    return redirect(url_for('book_bp.kitaplar'))