from core.database import db


class Yazar(db.Model):
    __tablename__ = "yazar"
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)
