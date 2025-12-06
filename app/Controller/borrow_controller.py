from flask import render_template, request, jsonify, redirect, url_for, flash, session, Blueprint
#from services.user_services import (user_login, add_user, change_password ,get_all_users)
#from services.book_services import (get_books, get_book_by_id, add_book, delete_book)
from services.borrow_services import ( request_borrow, get_pending_borrows, approve_borrow, reject_borrow,get_user_borrows, get_all_borrows, process_return)


borrow_bp = Blueprint('borrow_bp', __name__)

# --- Ödünç/İade Rotaları ---

@borrow_bp.route('/odunc', methods=['POST'])
def odunc_al():
    user_id = request.form.get('user_id')
    book_id = request.form.get('book_id')
    
    if not user_id or not book_id:
        flash("Eksik bilgi gönderildi", "danger")
        return redirect(url_for('borrow_bp.kitaplar'))
    
    try:
        user_id = int(user_id)
        book_id = int(book_id)
    except (TypeError, ValueError):
        flash("Geçersiz kullanıcı veya kitap ID", "danger")
        return redirect(url_for('borrow_bp.kitaplar'))
        
    success, mesaj = request_borrow(user_id, book_id) # İş Katmanı çağrısı
    
    if success:
        flash(mesaj, "info")
    else:
        flash(mesaj, "warning")
        
    return redirect(url_for("book_bp.kitap_detay", kitap_id=book_id))

@borrow_bp.route('/bekleyen_oduncler')
def bekleyen_oduncler():
    if session.get('rol') != 'personel':
        flash("Bu sayfayı sadece personel görebilir!", "danger")
        return redirect(url_for('borrow_bp.index'))

    oduncler = get_pending_borrows() # İş Katmanı çağrısı
    return render_template("bekleyen_oduncler.html", oduncler=oduncler)

@borrow_bp.route('/odunc_onayla/<int:odunc_id>', methods=['POST'])
def odunc_onayla(odunc_id):
    if session.get('rol') != 'personel':
        flash("Yetkiniz yok!", "danger")
        return redirect(url_for('borrow_bp.index'))
    
    success, mesaj, book_id = approve_borrow(odunc_id) # İş Katmanı çağrısı
    
    if success:
        flash(mesaj, "success")
    else:
        flash(mesaj, "danger")
        
    return redirect(url_for('borrow_bp.bekleyen_oduncler'))

@borrow_bp.route('/odunc_reddet/<int:odunc_id>', methods=['POST'])
def odunc_reddet(odunc_id):
    if session.get('rol') != 'personel':
        flash("Yetkiniz yok!", "danger")
        return redirect(url_for('borrow_bp.index'))
    
    success, mesaj = reject_borrow(odunc_id) # İş Katmanı çağrısı
    
    if success:
        flash(mesaj, "info")
    else:
        flash(mesaj, "danger")
        
    return redirect(url_for('borrow_bp.bekleyen_oduncler'))

@borrow_bp.route('/odunclerim')
def odunclerim():
    if 'user_id' not in session:
        flash("Ödünç kayıtlarınızı görmek için giriş yapmalısınız.", "warning")
        return redirect(url_for('borrow_bp.login_page'))
    
    user_id = session.get("user_id")
    liste = get_user_borrows(user_id) # İş Katmanı çağrısı
    return render_template("odunclerim.html", oduncler=liste, mode="all")

@borrow_bp.route("/late_borrows")
def late_borrows():
    if 'user_id' not in session:
        flash("Ödünç kayıtlarınızı görmek için giriş yapmalısınız.", "warning")
        return redirect(url_for('borrow_bp.login_page'))
    
    user_id = session.get("user_id")
    liste=get_all_borrows(user_id)
    return render_template("odunclerim.html", oduncler=liste, mode="late")

@borrow_bp.route('/tum_oduncler')
def tum_oduncler():
    if session.get('rol') != 'personel':
        flash("Bu sayfayı sadece personel görebilir!", "danger")
        return redirect(url_for('borrow_bp.index'))
    
    mode = request.args.get('mode', 'liste') 
    liste = get_all_borrows() # İş Katmanı çağrısı
   
    if mode == "iade":
        liste = [o for o in liste if o["durum"] != "iade_edildi"]

    if not liste:
        flash("Ödünç kaydı yok!", "info")
    return render_template("tum_oduncler.html", oduncler=liste, mode=mode)

@borrow_bp.route('/iade_al/<int:odunc_id>', methods=['GET','POST'])
def iade_al(odunc_id):
    if session.get('rol') != 'personel':
        flash("Bu işlemi yapmaya yetkiniz yok!", "danger")
        return redirect(url_for('borrow_bp.index'))
        
    if request.method == 'POST':
        success, mesaj = process_return(odunc_id)
        if success:
            flash(mesaj, "success")
        else:
            flash(mesaj, "warning")
    #liste = get_all_borrows()
    #  return render_template("iade_al.html", oduncler=liste)
    return redirect(url_for('borrow_bp.tum_oduncler' , mode='iade'))