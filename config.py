import os
class Config:
    #bağlantı ayarları
        # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey123")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:Zehra123.@localhost/kutuphane"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Iyzipay (Sandbox test ortamı)
    IYZI_PUBLIC_KEY = "sandbox-xPQYH1ycPAsQXVmnU0jLfXyhE50dqH5d"
    IYZI_SECRET_KEY = "sandbox-iGCo7YDvGXxpGaXFnEPXfPOaOaPxUc0D"
    IYZI_BASE_URL = "sandbox-api.iyzipay.com"
