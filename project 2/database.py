import sqlite3

class Database:
    def __init__(self, db_name="game_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        # Drop existing tables to recreate with new schema
        self.cur.execute("DROP TABLE IF EXISTS progress")
        self.create_table()
        self.create_user_table()
        self.create_tables()

    def create_table(self):
        """Creates a table to store game progress if it doesn't exist."""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                level INTEGER NOT NULL,
                score INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def create_user_table(self):
        """Creates a table to store user data if it doesn't exist."""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_user(self, username, password):
        """Adds a new user to the database."""
        self.cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()

    def check_user(self, username, password):
        """Checks if the user exists in the database."""
        self.cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        return self.cur.fetchone() is not None

    def save_progress(self, username, level, score=0):
        """Saves the player's progress to the database."""
        self.cur.execute("""
            INSERT INTO progress (username, level, score) 
            VALUES (?, ?, ?)
        """, (username, level, score))
        self.conn.commit()

    def get_latest_level(self, username=None):
        """Gets the highest level the player has completed."""
        if username:
            self.cur.execute("SELECT MAX(level) FROM progress WHERE username = ?", (username,))
        else:
            self.cur.execute("SELECT MAX(level) FROM progress")
        result = self.cur.fetchone()
        return result[0] if result[0] is not None else 1  # Default to level 1 if no progress

    def get_high_score(self, username=None):
        """Gets the player's highest score."""
        if username:
            self.cur.execute("SELECT MAX(score) FROM progress WHERE username = ?", (username,))
        else:
            self.cur.execute("SELECT MAX(score) FROM progress")
        result = self.cur.fetchone()
        return result[0] if result[0] is not None else 0

    def reset_progress(self):
        """Resets the progress (for restarting the game)."""
        self.cur.execute("DELETE FROM progress")
        self.conn.commit()

    def close(self):
        """Closes the database connection."""
        self.conn.close()

    def check_username_exists(self, username):
        """Check if a username already exists in the database."""
        self.cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        return self.cur.fetchone() is not None

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            current_level INTEGER DEFAULT 1,
            high_score INTEGER DEFAULT 0
        )''')
        
        # Add new table for history
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            username TEXT,
            level INTEGER,
            score INTEGER,
            time_taken REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )''')
        self.conn.commit()

    def add_history_entry(self, username, level, score, time_taken):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO history (username, level, score, time_taken)
        VALUES (?, ?, ?, ?)
        ''', (username, level, score, time_taken))
        self.conn.commit()

    def get_user_history(self, username):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT date, level, score, time_taken 
        FROM history 
        WHERE username = ? 
        ORDER BY date DESC
        ''', (username,))
        return cursor.fetchall()
