from flask_sqlalchemy import SQLAlchemy
import pymysql

db = SQLAlchemy()

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Zehra123.",
        database="kutuphane",
        cursorclass=pymysql.cursors.DictCursor
    )
