from core.database import db
from datetime import datetime


class EmailQueue(db.Model):
    __tablename__ = 'email_queue'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subjectt = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipient_email = db.Column(db.String(120), nullable=True) # E-posta adresini tutacak sütun
