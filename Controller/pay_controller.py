from unittest import result
from flask import Blueprint, jsonify, render_template, request, redirect, session, url_for, flash
import iyzipay
from entity.user_entity import User  
from entity.borrow_entity import Borrow # kendi modellerini buraya ekle
from core.database import db
from config import Config
pay_bp = Blueprint("pay_bp", __name__)
import json


options = {
    "api_key": Config.IYZI_PUBLIC_KEY,
    "secret_key": Config.IYZI_SECRET_KEY,
    "base_url": Config.IYZI_BASE_URL
}
@pay_bp.route("/ceza_ode/<int:user_id>", methods=["GET","POST"])
def ceza_ode(user_id):
    penalties=Borrow.query.filter(Borrow.user_id==user_id, Borrow.ceza >0).all()
    total_ceza = sum(b.ceza for b in penalties)

    if request.method == "GET":
        return render_template("ceza_ode.html", total_ceza=total_ceza, penalties=penalties, user_id=user_id)
    
    card_name = request.form.get("card_name")
    card_number = request.form.get("card_number")
    month = request.form.get("month")
    year = request.form.get("year")
    cvv = request.form.get("cvv")

    payment_request={
    "locale": "tr",
    "conversationId": str(user_id),
    "price": str(total_ceza),
    "paidPrice": str(total_ceza),
    "currency": "TRY",
    "installment": 1,
    "basketId": str(user_id),
    "paymentChannel": "WEB",
    "paymentGroup": "PRODUCT",
    "callbackUrl": "http://127.0.0.1:5000/payment_callback",
    "paymentCard": {
        "cardHolderName": card_name,
        "cardNumber": card_number,
        "expireMonth": month,
        "expireYear": year,
        "cvc": cvv,
        "registerCard": 0
    },
    "buyer": {
        "id": str(user_id),
        "name": User.query.get(user_id).isim,
        "surname": User.query.get(user_id).isim,
        "gsmNumber": "+905555555555",
        "email": User.query.get(user_id).email,
        "identityNumber": "11111111111",
        "lastLoginDate": "2023-12-10 12:00:00",
        "registrationDate": "2023-12-10 12:00:00",
        "registrationAddress": "Türkiye",
        "ip": "85.34.78.112",
        "city": "Istanbul",
        "country": "Turkey",
        "zipCode": "34000"
    },
        "shippingAddress": {
        "contactName": "Zehra Gül",
        "city": "Istanbul",
        "country": "Turkey",
        "address": "Kullanıcı Adresi",
        "zipCode": "34000"
    },
    "billingAddress": {
        "contactName": "Kullanıcı",
        "city": "Istanbul",
        "country": "Turkey",
        "address": "Test Address",
        "zipCode": "34000"
    },
    "basketItems": [
        {
            "id": "CEZA",
            "name": "Kitap cezası",
            "category1": "Kütüphane",
            "itemType": "VIRTUAL",
            "price": str(total_ceza)
        }
    ]
}
    print("OPTIONS:", options) 
    payment = iyzipay.CheckoutFormInitialize().create(payment_request, options)

# iyzipay objesini stringe çevir
    result = payment.read().decode("utf-8")

# JSON'a çevir
    json_data = json.loads(result)
    print(json_data)

    if json_data.get("status") != "success":
        return jsonify({
            "status": "error",
            "message": json_data.get("errorMessage", "Ödeme başlatılamadı.")
        }), 400


    return redirect(json_data["paymentPageUrl"])


@pay_bp.route("/payment_callback", methods=["POST"])
def payment_callback():
    print("CALLBACK GELDİ:", request.form)

    token = request.form.get("token")
    if not token:
        return "token bulunamadı", 400

    # Token ile ödemeyi sorgula
    request_data = {
        "locale": "tr",
        "token": token
    }

    payment_result = iyzipay.CheckoutForm().retrieve(request_data, options)
    result = json.loads(payment_result.read().decode())

    print("İYZİCO RESULT:", result)

    if result.get("paymentStatus", "").lower() != "success":
        return "Ödeme başarısız", 400

    basket_id = result.get("basketId")

    if not basket_id and "itemTransactions" in result:
        basket_id = result["itemTransactions"][0].get("itemId")

    if not basket_id:
        return "Kullanıcı ID tespit edilemedi (basketId yok)", 400

    user_id = int(basket_id)



    # Ceza silme işlemi
    penalties = Borrow.query.filter(Borrow.user_id == user_id, Borrow.ceza > 0).all()
    for b in penalties:
        b.ceza = 0
        b.durum = "iade_edildi"
    db.session.commit()

    flash("Ödeme başarılı!", "success")
    return redirect(url_for("pay_bp.ceza_ode", user_id=user_id))

