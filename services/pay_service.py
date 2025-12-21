from entity.user_entity import User
from entity.borrow_entity import Borrow
from core.database import db
import iyzipay
import json
from config import Config

#Iyzipay’e yapılacak tüm isteklerde kullanılacak kimlik bilgileri
options = {
    "api_key": Config.IYZI_PUBLIC_KEY,
    "secret_key": Config.IYZI_SECRET_KEY,
    "base_url": Config.IYZI_BASE_URL
}
#Kullanıcı ve toplam cezaları getir
def get_user_and_penalties(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, []
    penalties = Borrow.query.filter(Borrow.user_id==user_id, Borrow.ceza>0).all()
    return user, penalties

def calculate_total_ceza(penalties):
    return sum(b.ceza for b in penalties)

#Iyzipay ödeme request objesi
def create_payment_request(user, total_ceza, card_data):
    return {
        "locale": "tr",
        "conversationId": str(user.id),
        "price": str(total_ceza),
        "paidPrice": str(total_ceza),
        "currency": "TRY",
        "installment": 1,
        "basketId": str(user.id),
        "paymentChannel": "WEB",
        "paymentGroup": "PRODUCT",
        "callbackUrl": "http://127.0.0.1:5000/payment_callback",
        "paymentCard": card_data,
        "buyer": {
            "id": str(user.id),
            "name": user.isim,
            "surname": user.isim,
            "gsmNumber": "+905555555555",
            "email": user.email,
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
            "contactName": user.isim,
            "city": "Istanbul",
            "country": "Turkey",
            "address": "Kullanıcı Adresi",
            "zipCode": "34000"
        },
        "billingAddress": {
            "contactName": user.isim,
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

#Ödeme isteğini iyzipay ile başlatır
def initialize_payment(user, total_ceza, card_data):
    payment_request = create_payment_request(user, total_ceza, card_data)
    payment = iyzipay.CheckoutFormInitialize().create(payment_request, options)
    result = json.loads(payment.read().decode("utf-8"))
    return result

#Callback sonrası ödeme kontrol ve ceza sıfırlama
def process_payment_callback(token):
    request_data = {"locale":"tr","token":token}
    payment_result = iyzipay.CheckoutForm().retrieve(request_data, options)
    result = json.loads(payment_result.read().decode("utf-8"))

    if result.get("paymentStatus","").lower() != "success":
        return False, "Ödeme başarısız", None

    user_id = int(result.get("basketId"))
    Borrow.query.filter(Borrow.user_id==user_id, Borrow.ceza>0).update({"ceza":0})
    db.session.commit()
    return True, "Ödeme başarılı", user_id
