import os
from flask import Flask, render_template, session
import uvicorn

from asgiref.wsgi import WsgiToAsgi
from flask_wtf import CSRFProtect

# Custom modules
from auth.mfa import mfa_bp
from db import close_db
from auth.routes import auth_bp
from session_helpers import login_required, already_logged_in

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.register_blueprint(mfa_bp)
app.register_blueprint(auth_bp)

# CSRF Protection
csrf = CSRFProtect(app)
csrf.init_app(app)

# Logging configuration
debug_mode = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")


# Ensure database connection is closed after each request
@app.teardown_appcontext
def teardown_db(exception):
    close_db()


# Error handlers
@app.errorhandler(404)
def not_found_error(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    app.logger.exception("Internal server error")
    app.logger.exception(e)
    return render_template("500.html"), 500


# Routes
@app.route("/")
@already_logged_in
def index():
    return render_template("index.html"), 200


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user={"email": session.get("email")}), 200


asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)
