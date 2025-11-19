"""Database helper functions for the login daemon."""
import sqlite3
import hashlib
import secrets
from contextlib import contextmanager


DATABASE_NAME = 'users.db'


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_database():
    """Initialize the database with the users table."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                activation_token TEXT,
                is_activated INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_activation_token():
    """Generate a secure random activation token."""
    return secrets.token_urlsafe(32)


def create_user(username, password, email):
    """Create a new user with an activation token."""
    password_hash = hash_password(password)
    activation_token = generate_activation_token()
    
    with get_db_connection() as conn:
        try:
            conn.execute(
                'INSERT INTO users (username, password_hash, email, activation_token) VALUES (?, ?, ?, ?)',
                (username, password_hash, email, activation_token)
            )
            return activation_token
        except sqlite3.IntegrityError:
            return None


def activate_user(token):
    """Activate a user account using the activation token."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            'UPDATE users SET is_activated = 1, activation_token = NULL WHERE activation_token = ? AND is_activated = 0',
            (token,)
        )
        return cursor.rowcount > 0


def get_user_by_username(username):
    """Retrieve a user by username."""
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()


def verify_login(username, password):
    """Verify user login credentials."""
    user = get_user_by_username(username)
    if user and user['is_activated'] and user['password_hash'] == hash_password(password):
        return True
    return False
