from core.database import db
from datetime import datetime

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='borrows')
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    alis_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    iade_tarihi = db.Column(db.DateTime)
    gercek_iade_tarihi = db.Column(db.DateTime, nullable=True)
    ceza = db.Column(db.Float, default=0.0)
    gecikme_gun = db.Column(db.Integer, default=0)
    last_penalty_date = db.Column(db.Date)
    durum = db.Column(db.String(20), default='beklemede')
    book = db.relationship(
        'Book',
         backref=db.backref(
            'borrows',
            passive_deletes=True
        )
    )