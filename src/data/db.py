import sqlite3
import os
import json

DB_PATH= os.path.join(os.path.dirname(__file__), 'database.db')

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._create_tables()
    
    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TXT PRIMARY KEY,
                value TEXT NOT NULL
            )                  
        """)
        self.conn.commit()
    
    def set_setting(self, key, value):
        value_str = json.dumps(value)
        self.conn.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value_str))
        self.conn.commit()
    
    def get_setting(self, key, default=None):
        cursor = self.conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return default
    
    def close(self):
        self.conn.close()