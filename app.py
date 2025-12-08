import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
# from routes import main
from send_emails import send_email
from config import Config
from entity.user_entity import User
from entity.email_entity import EmailQueue
from core.database import db

import threading
import time
import pymysql


# Kendi modüllerimizi import ediyoruz

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Kütüphane init (Başlatma)
    db.init_app(app)
    Migrate(app, db)
    CORS(app)
    pymysql.install_as_MySQLdb()
    
    # Rotaları kaydet
    from Controller.user_controller import user_bp
    from Controller.book_controller import book_bp
    from Controller.borrow_controller import borrow_bp


    app.register_blueprint(user_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(borrow_bp)

    return app

def background_email_worker(app, db, EmailQueue, User):
    while True:
        with app.app_context():
            send_email(app, db, EmailQueue, User)
        time.sleep(10)  # her 10 saniyede bir mail kuyruğunu kontrol eder


if __name__ == "__main__":
    app = create_app()
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or os.environ.get("WERKZEUG_RUN_MAIN") is None:
        with app.app_context(): 

        # db.drop_all() # Gerekirse tüm tabloları siler
            db.create_all() # Tabloları oluşturur
            print("Veritabanı tabloları oluşturuldu.")
        import threading
# ... diğer importlar
# ... app, db, EmailQueue, User nesnelerinin tanımlandığı yer

# Gerekli argümanlar bir tuple olarak 'args' içine geçirilir.
        thread_args = (app, db, EmailQueue, User)

        email_thread = threading.Thread(
            target=background_email_worker, 
            args=thread_args
        ) 
        email_thread.daemon = True # Uygulama kapandığında thread'in de kapanmasını sağlar
        email_thread.start()

# app.run(...)    
    #threading.Thread(target=background_email_worker, daemon=True).start()
        app.run(
            debug=True,
            use_reloader=False # Yeniden yükleyiciyi devre dışı bırakır
        )