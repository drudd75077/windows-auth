"""
Main module for the project.
This contains all app configs and 
routes for this flask app
"""
from flask import Flask, render_template, request, redirect, session, url_for, flash, g, jsonify
import msal
import requests
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash 
from dotenv import load_dotenv
import os
from flask_session import Session
from .models import db, User


# Load environment variables from .flaskenv file
load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

#Initialize the db with the app
db.init_app(app)
migrate = Migrate(app, db)
# Set the server name explicitly to localhost:5000
app.config['SERVER_NAME'] = os.getenv('SERVER_NAME')



# Configure server-side session management
app.config['SESSION_TYPE'] = os.getenv('SESSION_TYPE')
app.config['SESSION_FILE_DIR'] = os.getenv('SESSION_FILE_DIR')
Session(app)

# Configuration
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
AUTHORITY = os.getenv('AUTHORITY')
REDIRECT_PATH = os.getenv('REDIRECT_PATH')
SCOPE = os.getenv('SCOPE').split()  # Split the scopes into a list

@app.before_request
def before_request():
    # Make user information available to all templates
    if 'user_oid' in session:
        g.user_oid = session['user_oid']
        g.user_email = session['user_email']
        g.display_name = session.get('display_name', '')  # Updated from first_name to display_name
    else:
        g.user_oid = None
        g.user_email = None
        g.display_name = None

@app.context_processor
def inject_user():
    return dict(
        user_oid=getattr(g, 'user_oid', None),
        user_email=getattr(g, 'user_email', None),
        display_name=getattr(g, 'display_name', None)  # Updated from first_name to display_name
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    display_name = request.form.get('display_name', '').strip()

    # Validate input
    is_valid, error_message = User.validate_registration(username, password, display_name)
    if not is_valid:
        flash(error_message, 'error')
        return redirect(url_for('register'))

    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash('Username already exists', 'error')
        return redirect(url_for('register'))

    try:
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, display_name=display_name)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during registration. Please try again.', 'error')
        return redirect(url_for('register'))
    
@app.route('/check_username', methods=['POST'])
def check_username():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Username is required'
            }), 400
        
        # Check if user exists in database
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'This username is not registered. Please contact the website administrator to register.'
            }), 404
        
        # User exists
        return jsonify({
            'success': True,
            'message': 'Username found'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

@app.route('/username_password_login', methods=['POST'])
def username_password_login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if not username or not password:
        flash('Both username and password are required', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        session['user_oid'] = username
        session['user_email'] = username
        session['display_name'] = user.display_name
        session['login_method'] = 'username_password'
        flash('Successfully authenticated!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Invalid username or password. Please contact the website administrator to reset your password.', 'error')
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/azure_login')
def azure_login():
    session["flow"] = _build_auth_code_flow(scopes=SCOPE)
    return redirect(session["flow"]["auth_uri"])

@app.route('/azure_logout')
def azure_logout():
    """Handle Azure logout process"""
    # Get the email that was used in the attempted login
    attempted_email = session.get('attempted_email', '')
    
    # Store the current flash messages in a temporary session key
    session['temp_flash_messages'] = session.get('_flashes', [])
    
    # Clear the session except for our temporary flash messages
    temp_messages = session['temp_flash_messages']
    session.clear()
    session['_flashes'] = temp_messages
    
    # Construct the Azure logout URL
    logout_url = (
        f"{AUTHORITY}/oauth2/v2.0/logout"
        f"?post_logout_redirect_uri={url_for('login', _external=True)}"
        f"&id_token_hint={session.get('id_token', '')}"  # Add the ID token hint
    )
    
    return redirect(logout_url)

@app.route(REDIRECT_PATH)
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        
        if "error" in result:
            error_msg = f"Authentication Error: {result.get('error')}"
            if 'error_description' in result:
                error_msg += f" - {result.get('error_description')}"
            
            flash(error_msg, 'error')
            return redirect(url_for('azure_logout'))
        
        claims = result.get('id_token_claims', {})
        print("Claims received:", claims)  # Keep this for debugging
        
        # Store the ID token for logout
        session['id_token'] = result.get('id_token', '')
        
        oid = claims.get('oid')
        email = claims.get('preferred_username')
        
        if not oid or not email:
            flash('Failed to get user information from authentication response', 'error')
            return redirect(url_for('azure_logout'))

        # Store the email that was attempted to be used for login
        session['attempted_email'] = email

        # Check if a user exists with username matching the email
        from sqlalchemy import select
        user = db.session.execute(
            select(User).filter_by(username=email)
        ).scalar_one_or_none()

        if not user:
            flash(f'No local account found matching your Azure email ({email}). Please contact your administrator to register.', 'error')
            return redirect(url_for('azure_logout'))
        
        # User found, use their information from our database
        display_name = user.display_name  # Updated from first_name to display_name
        
        # Clear the attempted_email since login was successful
        session.pop('attempted_email', None)
        
        # Store user information in session
        session['user_oid'] = oid
        session['user_email'] = email
        session['display_name'] = display_name  # Updated from first_name to display_name
        session['login_method'] = 'azure'
        session['user_id'] = user.id
        flash('Successfully authenticated!', 'success')
        _save_cache(cache)
        
        return redirect(url_for('index'))
        
    except ValueError as e:
        flash(f'Authentication error: {str(e)}', 'error')
        return redirect(url_for('azure_logout'))
    except Exception as e:
        flash(f'Unexpected error during authentication: {str(e)}', 'error')
        print("Full error details:", e)  # Keep this for debugging
        return redirect(url_for('azure_logout'))

# Update the regular logout route to handle both types of logout
@app.route('/logout')
def logout():
    login_method = session.get('login_method')
    if login_method == 'azure':
        return redirect(url_for('azure_logout'))
    else:
        session.clear()
        flash('You have been logged out successfully', 'success')
        return redirect(url_for('login'))

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=authority or AUTHORITY,
        client_credential=CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    redirect_uri = url_for("authorized", _external=True)
    print(f"Redirect URI: {redirect_uri}")
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=redirect_uri)

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()