# Login Daemon

A basic login daemon built with Flask, featuring user registration, email-based account activation, and authentication.

## Features

- **User Registration**: Users can sign up with a username, email, and password
- **Account Activation**: Email-based activation system using secure tokens
- **User Authentication**: Login and logout functionality
- **Password Security**: Passwords are hashed using SHA-256
- **Session Management**: Flask sessions for maintaining user login state
- **Responsive UI**: Clean, modern interface with flash messages
- **Form Validation**: Client-side and server-side validation

## Project Structure

```
project/
├── app.py                        # Main Flask application
├── db.py                         # Database helper functions
├── init_db.py                    # Database initialization script
├── requirements.txt              # Python dependencies
├── static/
│   └── main.js                   # Client-side JavaScript
└── templates/
    ├── base.html                 # Base template with styling
    ├── register.html             # Registration form
    ├── activation_success.html   # Successful activation page
    └── activation_error.html     # Failed activation page
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/e1kfL0ck/app-sec-login-daemon.git
   cd app-sec-login-daemon
   ```

2. **Install dependencies**:
   ```bash
   pip install -r project/requirements.txt
   ```

3. **Initialize the database**:
   ```bash
   python project/init_db.py
   ```

## Usage

### Running the Application

**Production mode** (debug disabled):
```bash
python project/app.py
```

**Development mode** (debug enabled):
```bash
DEBUG=true python project/app.py
```

The application will be available at: http://localhost:5000

### User Flow

1. **Register**: Navigate to `/register` and create a new account
2. **Activate**: Click the activation link provided after registration
3. **Login**: Use your credentials to log in at `/login`
4. **Logout**: Click the logout link when logged in

## API Endpoints

- `GET /` - Home page
- `GET /register` - Registration form
- `POST /register` - Submit registration
- `GET /activate/<token>` - Activate account
- `GET /login` - Login form
- `POST /login` - Submit login credentials
- `GET /logout` - Logout user

## Security Features

- ✅ Passwords hashed with SHA-256
- ✅ Secure random token generation for activation
- ✅ Debug mode disabled by default
- ✅ Session-based authentication
- ✅ Input validation
- ✅ SQLite database with parameterized queries (SQL injection prevention)

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    activation_token TEXT,
    is_activated INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Development

### Running Tests

The application can be tested manually by:
1. Registering a new user
2. Verifying the activation token in the database
3. Activating the account via the activation link
4. Logging in with the credentials

### Environment Variables

- `DEBUG` - Set to `true` to enable Flask debug mode (default: `false`)

## Technologies Used

- **Backend**: Python 3, Flask 3.0.0
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **Security**: Werkzeug (password hashing), secrets (token generation)

## License

This project is provided as-is for educational purposes.

## Notes

- The database file `users.db` is created automatically when you run `init_db.py`
- In a production environment, consider:
  - Using a production WSGI server (e.g., Gunicorn)
  - Implementing actual email sending for activation links
  - Using stronger password hashing (e.g., bcrypt, Argon2)
  - Adding HTTPS support
  - Implementing rate limiting
  - Adding CSRF protection
  - Using environment variables for configuration
