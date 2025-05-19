from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "catalog.db"

# Inicializar DB se não existir
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                duration INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/videos', methods=['POST'])
def create_video():
    data = request.get_json()
    if not data or not all(k in data for k in ("title", "description", "duration")):
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO videos (title, description, duration)
        VALUES (?, ?, ?)
    ''', (data['title'], data['description'], data['duration']))
    conn.commit()
    video_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": video_id, **data}), 201

@app.route('/videos', methods=['GET'])
def get_videos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, duration FROM videos')
    rows = cursor.fetchall()
    conn.close()

    videos = [{"id": row[0], "title": row[1], "description": row[2], "duration": row[3]} for row in rows]
    return jsonify(videos), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)