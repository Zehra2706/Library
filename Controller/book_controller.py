from flask import g, render_template, request, jsonify, redirect, url_for, flash, session, Blueprint
from auth import token_required
from repository import category_repository
from repository import yazar_repository
from services import book_services
from services.book_services import (add_category, add_yazar, get_books, get_book_by_id, delete_book)


book_bp = Blueprint('book_bp', __name__, template_folder='templates')

@book_bp.route('/')
def index():
    return render_template("index.html")

@book_bp.route('/api/kitaplar', methods=['GET'])
@token_required
def api_kitaplar():
    q = request.args.get("q", "")
    kitaplar = get_books(q)
    return jsonify(kitaplar), 200

@book_bp.route('/kitaplar')
@token_required
def kitaplar():
    q = request.args.get("q", "")
    kitaplar_json_listesi = get_books(q) # İş Katmanı çağrısı
    return render_template("kitaplar.html", kitaplar_data=kitaplar_json_listesi, arama=q)

@book_bp.route('/api/kitap/<int:kitap_id>', methods=['GET'])
@token_required
def api_kitap_detay(kitap_id):
    kitap = get_book_by_id(kitap_id)
    if not kitap:
        return jsonify({"hata": "Kitap bulunamadı"}), 404
    return jsonify(kitap.to_dict()), 200


@book_bp.route('/kitap/<int:kitap_id>')
@token_required
def kitap_detay(kitap_id):
    kitap_obj = get_book_by_id(kitap_id)
    if not kitap_obj:
        flash("Kitap bulunamadı.", "danger")
        return redirect(url_for('book_bp.kitaplar')) 
        
    return render_template('kitap_detay.html', kitap=kitap_obj.to_dict(), session=session)

@book_bp.route('/kitap_ekle_form', methods=['GET'])
@token_required
def kitap_ekle_form():
    kategoriler = category_repository.get_all()
    print(kategoriler)
    return render_template("kitap_ekle.html", kategoriler=kategoriler)

@book_bp.route('/kitap-form-gonder', methods=['POST'])
@token_required
def create_book():
    data = request.get_json()

    success, message = book_services.create_book(data)

    if success:
        return jsonify({"message": message}), 201
    else:
        return jsonify({"hata": message}), 400

@book_bp.route('/api/kitap_sil/<int:kitap_id>', methods=['DELETE'])
@token_required
def api_kitap_sil(kitap_id):
    if g.rol != "personel":
        return jsonify({"error": "Yetkisiz işlem"}), 403

    success, mesaj = delete_book(kitap_id)

    if success:
        return jsonify({"message": mesaj}), 200
    else:
        return jsonify({"error": mesaj}), 400

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

@book_bp.route('/api/kategoriler', methods=['GET'])
@token_required
def api_kategoriler():
    kategoriler = category_repository.get_all()
    return jsonify([
        {
            "id": k.id,
            "isim": k.isim
        } for k in kategoriler
    ]), 200

@book_bp.route('/kategori_ekle_form')
@token_required
def kategori_ekle_form():
    kategoriler = category_repository.get_all()
    return render_template('kategori_ekle.html', kategoriler=kategoriler)


@book_bp.route('/kategori-form-gonder', methods=['POST'])
@token_required
def kategori_form_gonder():
    try:
        data = request.get_json()

        if not data or "kategori_isim" not in data:
            return jsonify({"hata": "Kategori ismi boş olamaz"}), 400

        kategori_adi = data["kategori_isim"]
        # yeni = Category(isim=kategori_adi)


        if kategori_adi == "":
            return jsonify({"hata": "Kategori ismi boş olamaz"}), 400

        success, mesaj = add_category(kategori_adi)

        if success:
            return jsonify({"mesaj": mesaj}), 200
        else:
            return jsonify({"hata": mesaj}), 400

    except Exception as e:
        return jsonify({"hata": f"Sunucu hatası: {str(e)}"}), 500   

@book_bp.route('/api/kategori/<int:kategori_id>', methods=['DELETE'])
@token_required
def api_kategori_sil(kategori_id):

    if g.rol != "personel":
        return jsonify({"hata": "Yetkisiz işlem"}), 403

    # if category_repository.has_books(kategori_id):
    #     return jsonify({"hata": "Kategoriye ait kitaplar var"}), 400

    kategori = category_repository.get_by_id(kategori_id)
    if not kategori:
        return jsonify({"hata": "Kategori bulunamadı"}), 404

    success, mesaj = category_repository.delete(kategori)

    if success:
        return jsonify({"mesaj": mesaj}), 200
    else:
        return jsonify({"hata": mesaj}), 400


@book_bp.route('/kategori/sil/<int:kategori_id>' , methods=['POST'])
@token_required 
def kategori_sil_html(kategori_id):
    if g.rol != "personel":
        flash("Bu işlemi yapmaya yetkiniz yok!", "danger")
        return redirect(url_for('book_bp.index'))
    kategori = category_repository.get_by_id(kategori_id)
    if not kategori:
        return jsonify({"hata": "Kategori bulunamadı!"}), 404

    success, mesaj = category_repository.delete(kategori) # İş Katmanı çağrısı
    if success:
        flash(mesaj, "success")
    else:
        flash(mesaj, "danger")
        
    return redirect(url_for('book_bp.kategori_ekle_form'))

@book_bp.route('/api/yazarlar', methods=['GET'])
@token_required
def api_yazarlar():
    yazarlar = yazar_repository.get_all()
    return jsonify([y.to_dict() for y in yazarlar]), 200

@book_bp.route('/yazar_ekle_form')
@token_required
def yazar_ekle_form():
    yazarlar = yazar_repository.get_all()
    return render_template('yazar_ekle.html', yazarlar=yazarlar)

@book_bp.route('/yazar-form-gonder', methods=['POST'])
@token_required
def yazar_form_gonder():
    try:
        data = request.get_json()

        if not data or "yazar_isim" not in data:
            return jsonify({"hata": "Yazar ismi boş olamaz"}), 400

        yazar_adi = data["yazar_isim"]
        # yeni = Yazar(isim=yazar_adi)

        if yazar_adi == "":
            return jsonify({"hata": "Yazar ismi boş olamaz"}), 400

        success, mesaj = add_yazar(yazar_adi)

        if success:
            return jsonify({"mesaj": mesaj}), 200
        else:
            return jsonify({"hata": mesaj}), 400

    except Exception as e:
        return jsonify({"hata": f"Sunucu hatası: {str(e)}"}), 500   

@book_bp.route('/api/yazar_sil/<int:yazar_id>', methods=['DELETE'])
@token_required
def api_yazar_sil(yazar_id):

    if g.rol != "personel":
        return jsonify({"hata": "Yetkisiz işlem"}), 403

    yazar = yazar_repository.get_by_id(yazar_id)
    if not yazar:
        return jsonify({"hata": "Yazar bulunamadı"}), 404

    success, mesaj = yazar_repository.delete(yazar)

    if success:
        return jsonify({"mesaj": mesaj}), 200
    else:
        return jsonify({"hata": mesaj}), 400


@book_bp.route('/yazar/sil/<int:yazar_id>' , methods=['POST'])
@token_required 
def yazar_sil_html(yazar_id):
    if g.rol != "personel":
        flash("Bu işlemi yapmaya yetkiniz yok!", "danger")
        return redirect(url_for('book_bp.index'))
    yazar = yazar_repository.get_by_id(yazar_id)
    if not yazar:
        return jsonify({"hata": "Kategori bulunamadı!"}), 404

    success, mesaj = yazar_repository.delete(yazar) # İş Katmanı çağrısı
    if success:
        flash(mesaj, "success")
    else:
        flash(mesaj, "danger")
        
    return redirect(url_for('book_bp.yazar_ekle_form'))