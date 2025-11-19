"""Basic login daemon Flask application."""
from flask import Flask, render_template, request, redirect, url_for, session, flash
import db


app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'


# Initialize database on startup
with app.app_context():
    db.init_database()


@app.route('/')
def index():
    """Home page."""
    if 'username' in session:
        return f'<h1>Welcome, {session["username"]}!</h1><a href="/logout">Logout</a>'
    return '<h1>Login Daemon</h1><a href="/register">Register</a> | <a href="/login">Login</a>'


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if not username or not password or not email:
            flash('All fields are required!', 'error')
            return render_template('register.html')
        
        activation_token = db.create_user(username, password, email)
        
        if activation_token:
            # In a real application, send this link via email
            activation_link = url_for('activate', token=activation_token, _external=True)
            flash(f'Registration successful! Activation link: {activation_link}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username or email already exists!', 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/activate/<token>')
def activate(token):
    """Activate user account."""
    if db.activate_user(token):
        return render_template('activation_success.html')
    else:
        return render_template('activation_error.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if db.verify_login(username, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials or account not activated!', 'error')
    
    return '''
        <h2>Login</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
        <a href="/">Back</a>
    '''


@app.route('/logout')
def logout():
    """Logout user."""
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
