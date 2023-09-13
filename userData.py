import sqlite3 as sql

class Database:
    def __init__(self, db_name):
        self.db = sql.connect(db_name)
        self.cursor = self.db.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                state TEXT,
                data TEXT
            )
        """)

        self.db.commit()
    
    async def update_userdata(self, user, state, data):
        existing_user = self.cursor.execute(f"SELECT user_id FROM users WHERE user_id == {user.id}").fetchone()
        if existing_user is None:
            if user.username is not None:
                username = user.username
            else:
                username = '-' + user.first_name + '-'

            self.cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (user.id, username, state, data))
            self.db.commit()
        else:
            self.cursor.execute(f"UPDATE users SET state = '{state}', data = '{data}' WHERE user_id == {user.id}")
            self.db.commit()

    async def get_userdata(self, user_id):
        data = self.cursor.execute(f"SELECT state, data FROM users WHERE user_id == {user_id}").fetchone()
        if data is not None:
            return data
        else:
            return ('', '{}')
        
    async def get_users(self):
        users = self.cursor.execute("SELECT user_id FROM users").fetchall()
        return users


users_info = Database('users.db')