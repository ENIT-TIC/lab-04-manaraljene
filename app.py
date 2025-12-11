from flask import Flask, jsonify, request
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

DB_PATH = "/app/data/books.db"

# Initialize the SQLite database
def init_db():
    os.makedirs("/app/data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Books API",
        "version": "2.0 - SQLite",
        "endpoints": {
            "GET /books": "List all books",
            "GET /books/<id>": "Get a specific book",
            "POST /books": "Add a new book",
            "PUT /books/<id>": "Update a book",
            "DELETE /books/<id>": "Delete a book",
            "GET /health": "Health check"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/books', methods=['GET'])
def get_books():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author, year FROM books")
    rows = cursor.fetchall()
    conn.close()

    books_list = [
        {"id": r[0], "title": r[1], "author": r[2], "year": r[3]}
    for r in rows]

    return jsonify({"books": books_list, "count": len(books_list)})

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author, year FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"id": row[0], "title": row[1], "author": row[2], "year": row[3]})

    return jsonify({"error": "Book not found"}), 404

@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    if not data or not all(k in data for k in ['title', 'author', 'year']):
        return jsonify({"error": "Missing required fields"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
        (data["title"], data["author"], data["year"])
    )
    conn.commit()

    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Book added",
        "id": new_id
    }), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Book not found"}), 404

    for field in ['title', 'author', 'year']:
        if field in data:
            cursor.execute(f"UPDATE books SET {field} = ? WHERE id = ?", (data[field], book_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Book updated"})

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({"message": "Book deleted successfully"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
