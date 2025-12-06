from flask import render_template, request, jsonify, redirect, url_for, flash, session, Blueprint
#from services.user_services import (user_login, add_user, change_password ,get_all_users)
from services.book_services import (get_books, get_book_by_id, add_book, delete_book)
#from services.borrow_services import ( request_borrow, get_pending_borrows, approve_borrow, reject_borrow,get_user_borrows, get_all_borrows, process_return)


book_bp = Blueprint('book_bp', __name__)

@book_bp.route('/kitap_ekle_form')
def kitap_ekle_form():
    return render_template('kitap_ekle.html')

@book_bp.route('/kitaplar')
def kitaplar():
    q = request.args.get("q", "")
    kitaplar_json_listesi = get_books(q) # İş Katmanı çağrısı
   # return redirect(url_for('book_bp.kitaplar')) 
   #print(kitaplar_json_listesi)
    return render_template("kitaplar.html", kitaplar_data=kitaplar_json_listesi, arama=q)

@book_bp.route('/kitap/<int:kitap_id>')
def kitap_detay(kitap_id):
    kitap_obj = get_book_by_id(kitap_id)
    if not kitap_obj:
        # get_or_404 kullanımı kaldırıldı, elle 404 döndürme veya redirect
        flash("Kitap bulunamadı.", "danger")
        return redirect(url_for('book_bp.kitaplar')) 
        
    return render_template('kitap_detay.html', kitap=kitap_obj.to_dict(), session=session)


@book_bp.route('/kitap-form-gonder', methods=['POST'])
def kitap_form_gonder():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ["baslik", "yazar", "kategori_id"]):
             return jsonify({"hata": "Eksik kitap bilgisi girdiniz."}), 400

        # Mevcut ve detay boş gelebilir, varsayılan değerler atanır.
        mevcut = data.get("mevcut", 0)
        detay = data.get("detay", None)
        image_url = data.get("image_url", None)
        
        success, mesaj = add_book(data["baslik"], data["yazar"], data["kategori_id"], mevcut, detay, image_url) # İş Katmanı çağrısı
        
        if success:
            return jsonify({"mesaj": mesaj}), 200
        else:
            return jsonify({"hata": mesaj}), 400
    except Exception as e:
        return jsonify({"hata": f"Sunucu hatası: {str(e)}"}), 500

@book_bp.route('/kitap/sil/<int:kitap_id>')
def kitap_sil_html(kitap_id):
    if session.get('rol') != 'personel':
        flash("Bu işlemi yapmaya yetkiniz yok!", "danger")
        return redirect(url_for('book_bp.kitaplar'))

    success, mesaj = delete_book(kitap_id) # İş Katmanı çağrısı
    if success:
        flash(mesaj, "success")
    else:
        flash(mesaj, "danger")
        
    return redirect(url_for('book_bp.kitaplar'))