import sqlite3
import os
from datetime import datetime
from .models import User

class UserDatabase:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with user table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Create saved_schedules table for future use
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    schedule_name TEXT NOT NULL,
                    schedule_data TEXT NOT NULL,
                    constraints_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()

    def create_user(self, username, email, password, first_name, last_name):
        """Create a new user"""
        try:
            password_hash = User.hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, first_name, last_name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, password_hash, first_name, last_name))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                return self.get_user_by_id(user_id)
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                raise ValueError("Username already exists")
            elif 'email' in str(e):
                raise ValueError("Email already exists")
            else:
                raise ValueError("User creation failed")

    def get_user_by_username(self, username):
        """Get user by username"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, password_hash, first_name, last_name, 
                       created_at, last_login
                FROM users WHERE username = ?
            ''', (username,))
            
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    first_name=row[4],
                    last_name=row[5],
                    created_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    last_login=datetime.fromisoformat(row[7]) if row[7] else None
                )
            return None

    def get_user_by_email(self, email):
        """Get user by email"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, password_hash, first_name, last_name, 
                       created_at, last_login
                FROM users WHERE email = ?
            ''', (email,))
            
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    first_name=row[4],
                    last_name=row[5],
                    created_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    last_login=datetime.fromisoformat(row[7]) if row[7] else None
                )
            return None

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, password_hash, first_name, last_name, 
                       created_at, last_login
                FROM users WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    first_name=row[4],
                    last_name=row[5],
                    created_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    last_login=datetime.fromisoformat(row[7]) if row[7] else None
                )
            return None

    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            conn.commit()

    def authenticate_user(self, username_or_email, password):
        """Authenticate user by username/email and password"""
        # Try to find user by username first, then by email
        user = self.get_user_by_username(username_or_email)
        if not user:
            user = self.get_user_by_email(username_or_email)
        
        if user and User.verify_password(password, user.password_hash):
            self.update_last_login(user.id)
            return user
        return None

    def get_user_count(self):
        """Get total number of users"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]