from flask import g, render_template, request, jsonify, redirect, url_for, flash,  Blueprint
from auth import token_required
from services.borrow_services import ( borrow_book, request_borrow, get_pending_borrows, approve_borrow, reject_borrow,get_user_borrows, get_all_borrows, process_return)
from repository.borrow_repository import toplam_ceza, wants_json_response
from flask import flash, redirect, url_for

borrow_bp = Blueprint('borrow_bp', __name__, template_folder='templates')

@borrow_bp.route('/')
def index():
    return redirect('/tum_oduncler')

@borrow_bp.route('/odunc', methods=['POST'])
@token_required
def odunc_al():
    user_id = request.form.get('user_id') or request.json.get('user_id')
    book_id = request.form.get('book_id') or request.json.get('book_id')

    if not user_id or not book_id:
        flash("Eksik bilgi gönderildi", "danger")
        return redirect(url_for('book_bp.kitaplar'))

    success, mesaj = borrow_book(user_id, book_id)  # Servis çağrısı

    if wants_json_response():
        return jsonify({"success": success, "message": mesaj})

    if success:
        flash(mesaj, "info")
    else:
        flash(mesaj, "warning")

    return redirect(url_for("book_bp.kitap_detay", kitap_id=book_id))

@borrow_bp.route('/api/bekleyen_oduncler')
@token_required
def api_bekleyen_oduncler():
    if g.rol != "personel":
        return jsonify({"success": False, "message": "Yetkiniz yok"}), 403
    oduncler = get_pending_borrows()
    return jsonify({"success": True, "oduncler": oduncler})

@borrow_bp.route('/bekleyen_oduncler')
@token_required
def bekleyen_oduncler():
    if g.rol != "personel":
        mesaj = "Bu sayfayı sadece personel görebilir!"
        if request.is_json:
            return jsonify({"success": False, "message": mesaj}), 403
        flash(mesaj, "danger")
        return redirect(url_for('borrow_bp.index'))

    oduncler = get_pending_borrows() # İş Katmanı çağrısı
    if request.is_json:
        return jsonify({"success": True, "oduncler": oduncler})

    return render_template("bekleyen_oduncler.html", oduncler=oduncler)

@borrow_bp.route('/odunc_onayla/<int:odunc_id>', methods=['POST'])
@token_required
def odunc_onayla(odunc_id):
    if g.rol != "personel":
        mesaj = "Yetkiniz yok!"
        if wants_json_response():
            return jsonify({"success": False, "message": mesaj}), 403
        flash(mesaj, "danger")
        return redirect(url_for('borrow_bp.index'))
    
    success, mesaj, book_id = approve_borrow(odunc_id) # İş Katmanı çağrısı
    
    if wants_json_response():
        return jsonify({"success": success, "message": mesaj, "book_id": book_id})

    if success:
        flash(mesaj, "success")
    else:
        flash(mesaj, "danger")
        
    return redirect(url_for('borrow_bp.bekleyen_oduncler'))

@borrow_bp.route('/odunc_reddet/<int:odunc_id>', methods=['POST'])
@token_required
def odunc_reddet(odunc_id):
    if g.rol != "personel":
        mesaj = "Yetkiniz yok!"
        if wants_json_response():
            return jsonify({"success": False, "message": mesaj}), 403
        flash(mesaj, "danger")
        return redirect(url_for('borrow_bp.index'))
    
    success, mesaj = reject_borrow(odunc_id) # İş Katmanı çağrısı
    
    if wants_json_response():
        return jsonify({"success": success, "message": mesaj})

    if success:
        flash(mesaj, "info")
    else:
        flash(mesaj, "danger")
        
    return redirect(url_for('borrow_bp.bekleyen_oduncler'))

@borrow_bp.route('/odunclerim')
@token_required
def odunclerim():
    if not getattr(g, "user_id", None):
        mesaj = "Ödünç kayıtlarınızı görmek için giriş yapmalısınız."
        if wants_json_response():
            return jsonify({"success": False, "message": mesaj}), 401
        flash(mesaj, "warning") 
        return redirect(url_for('user_bp.login_page'))
    
    user_id = g.user_id
    liste = get_user_borrows(user_id) # İş Katmanı çağrısı

    if wants_json_response():
        return jsonify({"success": True, "oduncler": liste})

    return render_template("odunclerim.html", oduncler=liste, mode="all")

@borrow_bp.route("/late_borrows")
@token_required
def late_borrows():
    if not getattr(g, "user_id", None):
        mesaj = "Ödünç kayıtlarınızı görmek için giriş yapmalısınız."
        if wants_json_response():
            return jsonify({"success": False, "message": mesaj}), 401
        flash(mesaj, "warning") 
        return redirect(url_for('user_bp.login_page'))
    
    user_id = g.user_id
    liste=get_all_borrows(user_id)

    if wants_json_response():
        return jsonify({"success": True, "oduncler": liste})

    return render_template("odunclerim.html", oduncler=liste, mode="late")

@borrow_bp.route('/tum_oduncler')
@token_required
def tum_oduncler():
    if g.rol != "personel":
        mesaj = "Ödünç kayıtlarını görmek için giriş yapmalısınız."
        if wants_json_response():
            return jsonify({"success": False, "message": mesaj}), 401
        flash(mesaj, "warning") 
        return redirect(url_for('borrow_bp.index'))
    
    mode = request.args.get('mode', 'liste') 
    liste = get_all_borrows() # İş Katmanı çağrısı
   
    if mode == "iade":
        liste = [o for o in liste if o["durum"] != "iade_edildi"]

    if not liste:
        flash("Ödünç kaydı yok!", "info")

    if wants_json_response():
        return jsonify({"success": True, "oduncler": liste}) 
       
    return render_template("tum_oduncler.html", oduncler=liste, mode=mode)

@borrow_bp.route('/iade_al/<int:odunc_id>', methods=['GET','POST'])
@token_required
def iade_al(odunc_id):
    if g.rol != "personel":
        flash("Bu işlemi yapmaya yetkiniz yok!", "danger")
        return redirect(url_for('borrow_bp.index'))
        
    if request.method == 'POST':
        success, mesaj = process_return(odunc_id)
        if success:
            flash(mesaj, "success")
        else:
            flash(mesaj, "warning")

    return redirect(url_for('borrow_bp.tum_oduncler' , mode='iade'))