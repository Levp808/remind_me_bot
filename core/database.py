import sqlite3

def get_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    
    conn.execute("CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY)")
    conn.execute("""
                CREATE TABLE IF NOT EXISTS events 
                (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 chat_id INTEGER NOT NULL,
                 title TEXT,
                 event_dt TEXT NOT NULL
                )
                """)
    conn.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_clean_expired
                BEFORE INSERT ON events
                BEGIN
                    DELETE FROM events
                    WHERE id IN (
                        SELECT id FROM events
                        WHERE event_dt <= strftime('%Y-%m-%d %H:%M','now','localtime')
                        LIMIT 5
                    );
                END;
                """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_event_dt ON events (event_dt)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_id ON events (chat_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_id ON users (chat_id)")
    conn.commit()

    return conn

# --- Утилиты БД ---

# Проверяет, существует ли пользователь в БД
def user_exists(conn, chat_id):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE chat_id = ?", (chat_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (chat_id) VALUES (?)", (chat_id,))
        conn.commit()

def add_event(conn, chat_id, title, desc, dt_iso):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (chat_id, title, description, event_dt) VALUES (?, ?, ?, ?)",
                   (chat_id, title, desc, dt_iso))
    conn.commit()

def get_events(conn, chat_id):
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, event_dt FROM events WHERE chat_id = ?", (chat_id,))
    rows = cursor.fetchall()
    return rows

def delete_event(conn, event_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    return cursor.rowcount > 0
