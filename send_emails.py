import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime

# NOT: 'app.app_context()' çağrısı, bu fonksiyonu çağıran Thread tarafından yapılmalıdır (app.py'deki background_email_worker).
# Ancak fonksiyonun kendi içinde de tutarak tek başına çağrılabilmesini sağlıyoruz.

SMTP_USERNAME = "libraryysystem@gmail.com"
SMTP_PASSWORD = "pxwy wmvk jxxs rxsy" # Lütfen bu şifrenin Uygulama Şifresi olduğundan emin olun.

def send_email(app, db, EmailQueue, User):
    # Uygulama bağlamını koruyarak çalışmasını sağlıyoruz.
    with app.app_context():
        # 1. Gönderilmemiş en eski tek bir kaydı çek. Bu, kuyruk kilitlenmesini önler.
        mail = EmailQueue.query.filter_by(sent=0).order_by(EmailQueue.create_at.asc()).first()

        if mail is None:
            return # Kuyruk boşsa hemen çık

        recipient = None
        
        try:
            # --- 2. ALICI ADRESİNİ BELİRLEME MANTIĞI ---
            
            if mail.user_id is None:
                # Kullanıcı silinmiş: Adresi doğrudan recipient_email sütunundan al.
                recipient = mail.recipient_email 
                
                if not recipient:
                    # Kritik hata: Silinen kullanıcı kaydının adresi bile yok.
                    print(f"Hata: Silinmiş kullanıcı için alıcı adresi (recipient_email) boş. Kayıt atlanıyor. ID: {mail.id}")
                    # Hatalı kaydı sent=1 yaparak kuyruktan çıkarıyoruz.
                    mail.sent = 1
                    db.session.commit()
                    return

            else:
                # user_id mevcut: Kullanıcıyı çekip e-posta adresini kullan.
                user = User.query.get(mail.user_id)
                if user:
                    recipient = user.email
                else:
                    # Tutarsızlık: user_id var ama user tablosunda yok. Kaydı atla.
                    print(f"Hata: user_id {mail.user_id} ile kullanıcı bulunamadı. Kayıt atlanıyor. ID: {mail.id}")
                    mail.sent = 1
                    db.session.commit()
                    return

            # --- 3. GERÇEK SMTP GÖNDERİM İŞLEMİ ---
            
            msg = MIMEText(mail.body, 'html', 'utf-8')
            msg["Subject"] = Header(mail.subjectt, 'utf-8')
            msg["From"] = SMTP_USERNAME
            msg["To"] = recipient

            print(f"E-posta gönderiliyor: {mail.subjectt} -> {recipient}")
            
            # SMTP bağlantısını kur ve gönder
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(msg["From"], recipient, msg.as_string())
                
            # 4. BAŞARILI: Kaydı gönderildi olarak işaretle
            mail.sent = 1
            db.session.commit()
            print(f"E-posta başarıyla gönderildi ve işaretlendi. ID: {mail.id}")

        except Exception as e:
            # 5. HATA OLUŞTU: Oturumu geri al ve hatayı logla
            db.session.rollback()
            print(f"Kritik Gönderim/İşleme Hatası ({mail.id}): {e}")
            
            # NOT: Sürekli tekrar eden hataları önlemek için burada
            # mail.attempt_count gibi bir sütun kullanıp deneme sayısını artırmak
            # ve belirli bir sayıya ulaşınca göndermeyi durdurmak en iyisidir.
            # Şimdilik, sadece rollback yapıyoruz ki thread çökerse veritabanı oturumu kilitlenmesin.
