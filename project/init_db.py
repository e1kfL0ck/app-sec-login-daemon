"""Initialize the database for the login daemon."""
from db import init_database


if __name__ == '__main__':
    init_database()
    print('Database initialized successfully!')
