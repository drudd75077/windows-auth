import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask import Flask
from pathlib import Path  # Use Path for cross-platform compatibility

# Get the absolute path to the project root
ROOT_DIR = Path(__file__).resolve().parent.parent

# Create Flask app
app = Flask(__name__,
           template_folder=str(ROOT_DIR / 'templates'),
           static_folder=str(ROOT_DIR / 'static'))

# Load environment variables
from dotenv import load_dotenv
# Look for .env file in project root
load_dotenv(ROOT_DIR / '.flaskenv')

# Configure app
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('sqlite:///'):
    # Convert relative SQLite path to absolute path
    db_path = database_url.replace('sqlite:///', '')
    database_url = f'sqlite:///{ROOT_DIR / db_path}'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')

# Initialize database
from models import db, User
db.init_app(app)

def init_db():
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print(f"Database tables created successfully at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

            # Check if admin user already exists
            admin_user = User.query.filter_by(username='lwa_admin').first()
            if not admin_user:
                # Create admin user
                hashed_password = generate_password_hash('letsworkapps', method='pbkdf2:sha256')
                admin_user = User(
                    username='lwa_admin',
                    password=hashed_password,
                    display_name='LetsWorkApps_Admin'
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created successfully!")
                print("Username: lwa_admin")
                print("Password: letsworkapps")
                print("Display Name: LetsWorkApps_Admin")
            else:
                print("Admin user already exists!")

        except Exception as e:
            print(f"Error during database initialization: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    print(f"Initializing database at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Project root directory: {ROOT_DIR}")
    print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
    init_db()