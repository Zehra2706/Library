import mysql.connector
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Zehra123.",
        database="kutuphane"
    )
    print("Bağlantı başarılı")
except mysql.connector.Error as err:
    print("Hata:", err)

