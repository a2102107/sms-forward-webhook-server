from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from config import WEB_USERNAME, WEB_PASSWORD

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Login required to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if session.get('logged_in'):
        return redirect(url_for('index')) # Redirect to index if already logged in

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == WEB_USERNAME and password == WEB_PASSWORD:
            session['logged_in'] = True
            flash('Logged in successfully.', 'success')
            # Redirect to the page the user was trying to access, or index
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handles user logout."""
    session.pop('logged_in', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
