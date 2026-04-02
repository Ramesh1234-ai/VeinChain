from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import csv
from functools import wraps
import os
from flask import Flask, render_template
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Frontend/templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Frontend/static')
print("Template files:", os.listdir(template_dir))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
#----------------------------
@app.route('/')
def index_page():
     return render_template('adminPanel.html')
# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-change-this-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)
@app.before_first_request
def setup():
    print("App is starting up...")
# Blood compatibility matrix
BLOOD_COMPATIBILITY = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+']
}
# Helper Functions
def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or user.role not in required_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def calculate_next_eligible_date(last_donation_date):
    if last_donation_date:
        return last_donation_date + timedelta(days=90)  # 3 months gap
    return datetime.now().date()

def find_compatible_donors(blood_group, city, state):
    # Find donors who can donate to this blood group
    compatible_donors = []
    for donor_bg, can_donate_to in BLOOD_COMPATIBILITY.items():
        if blood_group in can_donate_to:
            # Find eligible donors
            today = datetime.now().date()
            donors = Donor.query.filter(
                Donor.blood_group == donor_bg,
                Donor.city == city,
                Donor.is_active == True,
                db.or_(
                    Donor.next_eligible_date == None,
                    Donor.next_eligible_date <= today
                )
            ).all()
            compatible_donors.extend(donors)
    
    return compatible_donors
# Routes
@app.route('/')
def index():
    return send_from_directory('.', 'bdms.html')
# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@bdms.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@bdms.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
app.run(debug=True, port=5000)