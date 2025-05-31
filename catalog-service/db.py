import sqlite3

DB_NAME = "catalog.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            duration INTEGER NOT NULL,
            views INTEGER DEFAULT 0,
            genre TEXT
        )
    ''')
    
    CREATE INDEX IF NOT EXISTS idx_video_genre ON videos (genre);
    CREATE INDEX IF NOT EXISTS idx_video_title ON videos(title);
     
    conn.commit()
    conn.close()
    

def get_all_videos():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM videos')
    rows = cursor.fetchall()
    
    videos = []
    
    for row in rows:
        videos.append({
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'duration': row['duration'],
            'views': row['views'],
            'genre': row['genre']
        })
    
     
    conn.close()
    return videos
    
def get_video_by_id(video_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos WHERE id = ?', (video_id))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'duration': row['duration'],
            'views': row['views'],
            'genre': row['genre']
        }
    return None

def create_video(title, description, duration, genre):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO videos (title, description, duration, genre)
        VALUES(?, ?, ?)    
        ''', (title, description, duration, genre))
    
    video_id = cursor.lastrowid
    conn.commit()
    conn.close()
        
    return video_id


def increment_view_count(video_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE videos SET views = views + 1 WHERE id = ?', (video_id,))
    
    row_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return row_count > 0