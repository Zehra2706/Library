import datetime
from core.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    parola = db.Column(db.String(300), nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    giris_tarihi = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # EKLENDİ
    temp_password = db.Column(db.Boolean, default=False)


    def to_dict(self):
        return {
            'id': self.id,
            'isim': self.isim,
            'email': self.email,
            'rol': self.rol,
            'giris_tarihi': self.giris_tarihi.strftime("%Y-%m-%d %H:%M") if self.giris_tarihi else None
        }