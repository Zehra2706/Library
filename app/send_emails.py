import smtplib
from email.mime.text import MIMEText

def send_email(app, db, EmailQueue, User):
    with app.app_context():
        mails = EmailQueue.query.filter_by(sent=0).all()

        for mail in mails:
            user = User.query.get(mail.user_id)
            if not user:
                continue

            msg = MIMEText(mail.body)
            msg["Subject"] = mail.subjectt
            msg["From"] = "libraryysystem@gmail.com"
            msg["To"] = user.email

            try:
                smtp = smtplib.SMTP("smtp.gmail.com", 587)
                smtp.starttls()
                smtp.login("libraryysystem@gmail.com", "pxwy wmvk jxxs rxsy")
                smtp.sendmail(msg["From"], msg["To"], msg.as_string())
                smtp.quit()

                mail.sent = 1
                db.session.commit()

            except Exception as e:
                print("Mail Gönderilemedi:", e)
