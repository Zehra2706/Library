from core.database import db
# from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    parola = db.Column(db.String(300), nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'isim': self.isim,
            'email': self.email,
            'rol': self.rol
        }