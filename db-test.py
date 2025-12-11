import sqlite3

DB_PATH = "books.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables existantes :", tables)
    conn.close()
    print("Connexion SQLite OK !")
except Exception as e:
    print("Erreur :", e)
