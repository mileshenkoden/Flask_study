import sqlite3
import time
from werkzeug.security import generate_password_hash

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.session.connection().connection.cursor()

    def addUser(self, name, email, password):
        try:
            self.__cur.execute("SELECT COUNT(*) as count FROM users WHERE email = ?", (email,))
            res = self.__cur.fetchone()
            if res and res[0] > 0:
                print("Користувач з таким email вже існує")
                return False

            hashed_password = generate_password_hash(password)
            tm = int(time.time())
            self.__cur.execute("INSERT INTO users (name, email, psw, date) VALUES (?, ?, ?, ?)", (name, email, hashed_password, tm))
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Помилка додавання користувача в БД:", str(e))
            return False

    def getUser(self, user_id):
        try:
            self.__cur.execute("SELECT * FROM users WHERE id = ? LIMIT 1", (user_id,))
            res = self.__cur.fetchone()
            if not res:
                print("Користувач не знайдений")
                return None
            return res
        except sqlite3.Error as e:
            print("Помилка отримання даних користувача з БД:", str(e))
            return None

    def getMenu(self):
        try:
            self.__cur.execute("SELECT * FROM menu")
            res = self.__cur.fetchall()
            return res if res else []
        except sqlite3.Error as e:
            print("Помилка отримання меню з БД: " + str(e))
            return []

    def getUserByEmail(self, email):
        try:
            self.__cur.execute("SELECT * FROM users WHERE email = ? LIMIT 1", (email,))
            res = self.__cur.fetchone()
            if not res:
                print("Користувача не знайдено")
                return None
            return res
        except sqlite3.Error as e:
            print("Помилка отримання даних з БД: " + str(e))
            return None
