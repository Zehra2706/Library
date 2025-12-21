from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from auth import token_required
from config import Config
from services.pay_service import calculate_total_ceza, get_user_and_penalties, initialize_payment, process_payment_callback
pay_bp = Blueprint("pay_bp", __name__)


#Ödemeyi yapar.
@pay_bp.route("/ceza_ode/<int:user_id>", methods=["GET","POST"])
@token_required
def ceza_ode(user_id):
    user, penalties = get_user_and_penalties(user_id)
    if not user:
        mesaj = "Kullanıcı bulunamadı"
        if request.is_json:
            return jsonify({"success": False, "message": mesaj}), 404
        flash(mesaj, "danger")
        return redirect(url_for("pay_bp.ceza_ode", user_id=user_id))

    total_ceza = calculate_total_ceza(penalties)

    if request.method == "GET":
        if request.is_json:
            return jsonify({"success": True, "total_ceza": total_ceza, "penalties": [b.__dict__ for b in penalties]})
        return render_template("ceza_ode.html", total_ceza=total_ceza, penalties=penalties, user_id=user_id)

    # POST -> ödeme isteği
    card_data = {
        "cardHolderName": request.form.get("card_name"),
        "cardNumber": request.form.get("card_number"),
        "expireMonth": request.form.get("month"),
        "expireYear": request.form.get("year"),
        "cvc": request.form.get("cvv"),
        "registerCard": 0
    }

    result = initialize_payment(user, total_ceza, card_data)

    if result.get("status") != "success":
        if request.is_json:
            return jsonify({"success": False, "message": result.get("errorMessage","Ödeme başlatılamadı.")}), 400
        flash(result.get("errorMessage","Ödeme başlatılamadı."), "danger")
        return redirect(url_for("pay_bp.ceza_ode", user_id=user_id))

    if request.is_json:
        return jsonify({
            "success": True,
            "message": "Ödeme sayfasına yönlendiriliyor",
            "paymentUrl": result["paymentPageUrl"]
        })
    return redirect(result["paymentPageUrl"])

#Ödeme sonrası sayfaya yönlendirir.
@pay_bp.route("/payment_callback", methods=["POST"])
def payment_callback():
    token = request.form.get("token")
    if not token:
        return "token bulunamadı", 400
    print(token)

    success, mesaj, user_id = process_payment_callback(token)
    if not success:
        return mesaj, 400
    
    if request.is_json:
        return jsonify({"success": False, "message": mesaj}), 404

    flash(mesaj, "success")
    return redirect(url_for("pay_bp.ceza_ode", user_id=user_id))
