from entity.email_entity import EmailQueue
from core.database import db

@staticmethod
def add(email):
        db.session.add(email)
        db.session.commit()

@staticmethod
def get_by_id(user_id):
        return EmailQueue.query.get(user_id)

#Belirli bir kullanıcıya ait tüm email kayıtlarını siler
def delete_by_user_id(user_id):
    try:
        EmailQueue.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return True, "Kullanıcıya ait email kayıtları silindi."
    except Exception as e:
        db.session.rollback()
        return False, str(e)

#Geçici şifre maili ekleme    
def add_temp_password_mail(user_id, email, temp_password):
    subject = "Geçici Şifreniz"
    body = f"""
    <h3>Şifre Sıfırlama</h3>
    <p>Geçici şifreniz:</p>
    <b>{temp_password}</b>
    <br><br>
    <p>Bu şifre ile giriş yaptıktan sonra lütfen yeni bir şifre belirleyiniz.</p>
    """
    #mail ekliyo
    mail = EmailQueue(
        user_id=user_id,
        subjectt=subject,
        body=body,
        recipient_email=email
    )

    db.session.add(mail)
    db.session.commit()



