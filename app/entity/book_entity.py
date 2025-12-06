from core.database import db
from entity.category_entity import Category

# from datetime import datetime


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(150), nullable=False)
    yazar = db.Column(db.String(150), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    kategori = db.relationship("Category", backref="kitaplar")
    mevcut = db.Column(db.Integer)
    image_url = db.Column(db.String(200), nullable=True)
    detay = db.Column(db.String(400), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'baslik': self.baslik or '',
            'yazar': self.yazar or '',
            'kategori_id': self.kategori_id or '',
            'mevcut': self.mevcut or '',
            'image_url': self.image_url or '',
            'detay': self.detay or 'Açıklama yok.',
            'kategori': self.kategori.isim if self.kategori else "Bilinmiyor"
        }