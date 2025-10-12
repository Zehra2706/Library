from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask çalışıyor!"

# MySQL bağlantı ayarları (şifre kısmını kendi şifrenle değiştir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Zehra123.@localhost/kutuphane'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)

class Student():
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    parola = db.Column(db.String(100), nullable=False)
    

        