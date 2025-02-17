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
import pyotp
import qrcode
import io
from base64 import b64encode

# Load environment variables from .flaskenv file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
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

def get_user_id_from_db(oid):
    # Placeholder function to get user ID from your user table based on the oid
    # Replace this with actual database queries
    user_table = {
        "your_user_oid_1": 1,
        "your_user_oid_2": 2,
        # Add more mappings as needed
    }
    return user_table.get(oid)

def generate_totp_uri(secret, user_email):
    return pyotp.totp.TOTP(secret).provisioning_uri(user_email, issuer_name="YourAppName")

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf)
    img_b64 = b64encode(buf.getvalue()).decode('utf-8')
    return img_b64

@app.route('/')
def index():
    user_id = session.get('user_id')
    user_email = session.get('user_email')
    return render_template('index.html', user_id=user_id, user_email=user_email)

@app.route('/login')
def login():
    session["flow"] = _build_auth_code_flow(scopes=SCOPE)
    return redirect(session["flow"]["auth_uri"])

@app.route(REDIRECT_PATH)
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        
        oid = result.get('id_token_claims').get('oid')
        email = result.get('id_token_claims').get('preferred_username')  # Use 'preferred_username' for email
        user_id = get_user_id_from_db(oid)
        
        # Clear the session and retain only the user ID and email
        session.clear()
        session['user_id'] = user_id
        session['user_email'] = email
        
        # Generate TOTP secret and add it to the session
        secret = pyotp.random_base32()
        session['totp_secret'] = secret
        
        # Redirect to 2FA setup page
        return redirect(url_for('setup_2fa'))
        
        _save_cache(cache)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/setup_2fa', methods=['GET', 'POST'])
def setup_2fa():
    if 'totp_secret' not in session:
        return redirect(url_for('index'))
    
    secret = session['totp_secret']
    user_email = session.get('user_email')
    totp_uri = generate_totp_uri(secret, user_email)
    qr_code = generate_qr_code(totp_uri)

    if request.method == 'POST':
        token = request.form.get('token')
        totp = pyotp.TOTP(secret)
        if totp.verify(token):
            session['2fa_verified'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid token. Please try again.')

    return render_template('setup_2fa.html', qr_code=qr_code)

@app.route('/logout')
def logout():
    session.clear()
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

if __name__ == "__main__":
    app.run(debug=True)