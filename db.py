import sqlite3
from config import DATABASE_PATH

def init_db():
    """Initializes the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_number TEXT,
            content TEXT,
            timestamp TEXT,
            received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            method TEXT,
            path TEXT,
            headers TEXT,
            body TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_message(from_number, content, timestamp, method, path, headers, body):
    """Inserts a new message into the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (from_number, content, timestamp, method, path, headers, body)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (from_number, content, timestamp, method, path, headers, body))
    conn.commit()
    conn.close()

def get_messages():
    """Fetches all messages from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Return rows as dictionary-like objects
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages ORDER BY received_at DESC')
    messages = cursor.fetchall()
    conn.close()
    # Convert rows to dictionaries for easier JSON serialization
    return [dict(row) for row in messages]

if __name__ == '__main__':
    init_db()
    print(f"Database initialized at {DATABASE_PATH}")
