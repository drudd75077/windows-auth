"""
Main module for the project.
This contains all app configs and 
routes for this flask app
"""
from flask import Flask, render_template, request, redirect, session, url_for, flash
import msal
import requests
from dotenv import load_dotenv
import os
from flask_session import Session
from datetime import datetime, timezone

# Load environment variables from .flaskenv file
load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.getenv('SECRET_KEY')

# Set the server name explicitly to localhost:5000
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['PREFERRED_URL_SCHEME'] = 'http'

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

@app.route('/')
def index():
    user_oid = session.get('user_oid')    # Changed from user_id to user_oid
    user_email = session.get('user_email')
    return render_template('index.html', 
                         user_oid=user_oid,  # Changed from user_id to user_oid
                         user_email=user_email)

@app.route('/login')
def login():
    session["flow"] = _build_auth_code_flow(scopes=SCOPE)
    return redirect(session["flow"]["auth_uri"])

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
            return redirect(url_for('index'))
        
        oid = result.get('id_token_claims', {}).get('oid')
        email = result.get('id_token_claims', {}).get('preferred_username')
        
        if not oid or not email:
            flash('Failed to get user information from authentication response', 'error')
            return redirect(url_for('index'))
        
        # Store the user information in session
        session['user_oid'] = oid      # Added this line
        session['user_email'] = email  # Added this line
        
        flash('Successfully authenticated!', 'success')
        _save_cache(cache)
        
        return redirect(url_for('index'))
        
    except ValueError as e:
        flash(f'Authentication error: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error during authentication: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(
        AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

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