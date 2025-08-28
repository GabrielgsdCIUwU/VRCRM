import sqlite3
import os
import json

DB_PATH= os.path.join(os.path.dirname(__file__), 'database.db')

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_tables()
    
    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TXT PRIMARY KEY,
                value TEXT NOT NULL
            )                  
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                isFriend bool NOT NULL DEFAULT TRUE
            )
        """)

        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                name TEXT PRIMARY KEY,
                color TEXT NOT NULL
            )
        """)
        
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS custom_messages (
                key TEXT PRIMARY KEY,
                text TEXT NOT NULL CHECK(length(text) <= 64),
                section TEXT NOT NULL CHECK(section IN ('message', 'response', 'request', 'requestResponse'))
            )
        """)


        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS vrchat_messages (
                slot INTEGER,
                message TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('message', 'response', 'request', 'requestResponse')),
                canBeUpdated BOOLEAN NOT NULL,
                PRIMARY KEY(slot, type)
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                invitation_type TEXT NOT NULL CHECK(invitation_type IN ('invite', 'inviteResponse', 'requestInvite')),
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                message TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        self.conn.commit()
    
    #region settings
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
    
    #region users
    def insert_user(self, user_id, name):
        self.conn.execute("INSERT INTO users (id, name) VALUES (?, ?)", (user_id, name))
        self.conn.commit()
    
    def delete_user(self, user_id):
        self.conn.execute("UPDATE users SET isFriend = ? WHERE id = ?", (False, user_id))
        self.conn.commit()
    
    def get_users(self):
        cursor = self.conn.execute("SELECT id, name FROM users")
        return cursor.fetchall()
    
    def user_exists(self, user_id):
        cursor = self.conn.execute("SELECT 1 FROM users WHERE id = ? LIMIT 1", (user_id,))
        return cursor.fetchone() is not None

    def update_who_is_not_friend(self, current_friend_ids):
        self.conn.execute("DROP TABLE IF EXISTS temp_current_friends")
        self.conn.execute("CREATE TEMP TABL temp_current_friends (id TEXT PRIMARY KEY)")
        self.conn.executemany("INSERT INTO temp_current_friends (id) VALUES (?)", [(id,) for id in current_friend_ids])

        self.conn.execute("""
            UPDATE users
            SET isFriend = FALSE
            WHERE id NOT IN (SELECT id FROM temp_current_friends)
        """)
        self.conn.commit()
    
    #region roles
    def insert_role(self, name, color):
        self.conn.execute("INSERT INTO roles (name, color) VALUES (?, ?)", (name, color))
        self.conn.commit()
    
    def delete_role(self, name):
        self.conn.execute("DELETE FROM roles WHERE name = ?", (name,))
        self.conn.commit()
    
    def get_roles(self):
        cursor = self.conn.execute("SELECT name, color FROM roles")
        return cursor.fetchall()
    
    #region custom messages
    def insert_custom_message(self, key, text, section):
        self.conn.execute("INSERT INTO custom_messages (key, text, section) VALUES (?, ?, ?)",  (key, text, section))
        self.conn.commit()
    
    def delete_custom_message(self, key):
        self.conn.execute("DELETE FROM custom_messages key = ?", (key,))
        self.conn.commit()
    
    def get_custom_messages(self, section=None):
        if section:
            cursor = self.conn.execute("SELECT key, text, section FROM custom_messages WHERE section = ?", (section,))
        else:
            cursor = self.conn.execute("SELECT key, text, section FROM custom_messages")
        return cursor.fetchall()
    
    #region vrchat messages
    def set_vrchat_message(self, slot, message, msg_type, canBeUpdated):
        self.conn.execute("""
            INSERT INTO vrchat_messages (slot, message, type, canBeUpdated)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(slot, type) DO UPDATE SET
                message=excluded.message,
                type=excluded.type,
                canBeUpdated=excluded.canBeUpdated
        """, (slot, message, msg_type, canBeUpdated))
        self.conn.commit()
    
    def can_update_vrchat_message(self, slot):
        cursor = self.conn.execute("""
            SELECT canBeUpdated FROM vrchat_messages
            WHERE slot = ?
            
        """, (slot,))
        row = cursor.fetchone()
        if not row:
            return True
        return bool(row["canBeUpdated"])
    
    def get_vrchat_messages(self):
        cursor = self.conn.execute("""
            SELECT slot, message, type, canBeUpdated FROM vrchat_messages
        """)
        return cursor.fetchall()
    
    def ensure_vrchat_messages(self, api, message_type="message"):
        user_id = api.get_user_id()
        messages = api.get_all_vrchat_messages(user_id, message_type)
        for msg in messages:
            self.set_vrchat_message(slot=msg["slot"], msg_type=msg["messageType"], message=msg["message"], canBeUpdated=msg["canBeUpdated"])

    #region logs
    def insert_log(self, user_id, invitation_type, date, message=None):
        print(f"Adding log: {user_id}, {invitation_type}, {date}, {message}")
            
        self.conn.execute("""
            INSERT INTO logs (user_id, invitation_type, timestamp, message) VALUES (?, ?, ?, ?)
        """, (user_id, invitation_type, date, message))
        
        self.conn.commit()
    
    def get_logs(self, limit=10, offset=0):
        cursor = self.conn.execute("""
            SELECT u.name, l.invitation_type, l.timestamp, l.message
            FROM logs as l JOIN users as u on l.user_id = u.id
            ORDER BY l.timestamp DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        return cursor.fetchall()
    
    def count_logs(self):
        cursor = self.conn.execute("SELECT COUNT(*) FROM logs")
        return cursor.fetchone()[0]

    def close(self):
        self.conn.close()