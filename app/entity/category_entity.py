from core.database import db


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)