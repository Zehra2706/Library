import os
class Config:
    #bağlantı ayarları
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey123")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "mysql+pymysql://root:Zehra123.@localhost/kutuphane")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
