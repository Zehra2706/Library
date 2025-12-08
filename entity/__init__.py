# from flask import Flask
# from config import Config
# from core.database import db

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
#     db.init_app(app)

#     from Controller.user_controller import user_bp
#     app.register_blueprint(user_bp)

#     return app
