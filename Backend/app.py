"""
VeinChain Backend - Refactored Application
Fixes all critical issues from code review
"""
import os
import uuid
import datetime
import ssl
import smtplib
import logging
from functools import wraps

# Flask imports
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Security imports
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from email.message import EmailMessage

# Firebase (optional)
try:
    from firebase_admin import auth, credentials, initialize_app
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

import jwt as pyjwt

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = FLASK_ENV == "development"

# Setup Flask app - SINGLE INSTANCE
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "Frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "..", "Frontend", "static")

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

# Configuration
app.secret_key = SECRET_KEY
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=1)
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = FLASK_ENV == "production"
app.config["SESSION_COOKIE_HTTPONLY"] = True

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///blood_donation.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

# CORS configuration - from environment
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500"
).split(",")
CORS(app, supports_credentials=True, origins=[o.strip() for o in cors_origins])

# Initialize extensions
Session(app)
JWTManager(app)

# Import models
from database import db, User, Donor, BloodRequest, Donation, ContactMessage, Notification

db.init_app(app)

# Initialize Firebase (optional)
FIREBASE_ENABLED = False
if FIREBASE_AVAILABLE:
    try:
        cred_path = os.path.join(BASE_DIR, "firebase_config.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            initialize_app(cred)
            FIREBASE_ENABLED = True
            logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.warning(f"Firebase initialization failed: {e}")

# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created/verified")


# ======================== #
# Utility Functions
# ======================== #

def generate_avatar(name):
    """
    Generate avatar URL using user's name initials.
    Uses Dicebear API (no authentication needed).
    """
    try:
        if not name:
            return "https://api.dicebear.com/7.x/initials/svg?seed=U"
        
        # Extract initials
        parts = name.split()
        initials = "".join([part[0].upper() for part in parts if part])
        
        # Use Dicebear API
        return f"https://api.dicebear.com/7.x/initials/svg?seed={initials}&scale=70"
    except Exception as e:
        logger.error(f"Avatar generation failed: {e}")
        return "https://api.dicebear.com/7.x/avataaars/svg?seed=default"


def send_notification(user, message):
    """Send notification to user via database and email."""
    try:
        # Save to database
        notif = Notification(
            id=str(uuid.uuid4()),
            user_id=user.id,
            message=message
        )
        db.session.add(notif)
        db.session.commit()
        
        # Send email if configured
        if not (EMAIL_USER and EMAIL_PASS):
            logger.warning("Email not configured, skipping email notification")
            return

        msg = EmailMessage()
        msg['Subject'] = "VeinChain Notification"
        msg['From'] = EMAIL_USER
        msg['To'] = user.email
        msg.set_content(message)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
            logger.info(f"Email notification sent to {user.email}")
    except Exception as e:
        logger.error(f"Notification failed: {e}", exc_info=True)


def token_required(f):
    """Decorator to require JWT token in Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            parts = token.split()
            if len(parts) != 2 or parts[0] != 'Bearer':
                return jsonify({'error': 'Invalid token format'}), 401
            
            token_str = parts[1]
            data = pyjwt.decode(token_str, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
                
        except pyjwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated


# ======================== #
# Authentication Routes
# ======================== #

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({'error': 'Email, name, and password are required'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'User already exists'}), 409
        
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            name=data['name'],
            email=data['email'],
            username=data.get('username') or data['email'],
            role=data.get('role', 'donor'),
            auth_method='local'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User registered: {user.email}")
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed: {e}", exc_info=True)
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with email and password."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            logger.warning(f"Failed login attempt for {email}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create token
        access_token = create_access_token(identity=user.id)
        
        # Store in session
        session['user'] = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
        
        logger.info(f"User logged in: {user.email}")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Login failed: {e}", exc_info=True)
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/auth/firebase-login', methods=['POST'])
def firebase_login():
    """Login using Firebase ID token."""
    if not FIREBASE_ENABLED:
        return jsonify({
            'error': 'Firebase not configured',
            'message': 'Place service account JSON at Backend/firebase_config.json'
        }), 503
    
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'Missing Firebase token'}), 400
        
        # Verify token with Firebase
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token['email']
        name = decoded_token.get('name', email.split("@")[0])
        
        # Fetch or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                name=name,
                email=email,
                username=email.split("@")[0],
                role='donor',
                auth_method='firebase'
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"New Firebase user created: {email}")
        
        # Generate JWT token for frontend
        access_token = create_access_token(identity=user.id)
        
        # Store in session
        session['user'] = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
        
        # Send notification
        send_notification(user, f"Welcome {user.name}! You logged in via Firebase.")
        
        return jsonify({
            'success': True,
            'message': 'Firebase login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Firebase login failed: {e}", exc_info=True)
        return jsonify({'error': 'Firebase login failed'}), 400


@app.route("/api/auth/status")
def auth_status():
    """Check authentication status."""
    if "user" in session:
        return jsonify({
            "logged_in": True,
            "user": session["user"]
        }), 200
    else:
        return jsonify({"logged_in": False}), 401


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """Logout user."""
    session.clear()
    logger.info("User logged out")
    return jsonify({"message": "Logged out successfully"}), 200


# ======================== #
# Donation Routes
# ======================== #

@app.route('/api/donations', methods=['POST'])
@token_required
def create_donation(current_user):
    """Create a new donation record."""
    try:
        if current_user.role != 'donor':
            return jsonify({'error': 'Only donors can create donations'}), 403
        
        data = request.get_json()
        
        # Validation
        required_fields = ['blood_type', 'quantity', 'location']
        if not all(data.get(field) for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        donation = Donation(
            id=str(uuid.uuid4()),
            donor_id=current_user.id,
            donation_date=datetime.datetime.utcnow(),
            blood_type=data['blood_type'],
            quantity=float(data['quantity']),
            location=data['location'],
            notes=data.get('notes', '')
        )
        
        # Update donor's last donation date
        donor = Donor.query.filter_by(user_id=current_user.id).first()
        if donor:
            donor.last_donation_date = datetime.datetime.utcnow()
        
        db.session.add(donation)
        db.session.commit()
        
        send_notification(
            current_user,
            f"Thanks {current_user.name}! Your donation of {donation.quantity}ml {donation.blood_type} has been recorded."
        )
        
        logger.info(f"Donation created: {donation.id} by {current_user.email}")
        
        return jsonify({'message': 'Donation recorded', 'donation_id': donation.id}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create donation failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create donation'}), 500


@app.route('/api/blood-requests', methods=['POST'])
@token_required
def create_blood_request(current_user):
    """Create a new blood request."""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['blood_type', 'quantity', 'urgency', 'hospital', 'contact_number']
        if not all(data.get(field) for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        blood_request = BloodRequest(
            id=str(uuid.uuid4()),
            requester_id=current_user.id,
            blood_type=data['blood_type'],
            quantity=float(data['quantity']),
            urgency=data['urgency'],
            hospital=data['hospital'],
            contact_number=data['contact_number'],
            notes=data.get('notes', ''),
            request_date=datetime.datetime.utcnow(),
            status='pending'
        )
        
        db.session.add(blood_request)
        db.session.commit()
        
        send_notification(
            current_user,
            f"Your request for {blood_request.quantity} units of {blood_request.blood_type} has been submitted."
        )
        
        logger.info(f"Blood request created: {blood_request.id} by {current_user.email}")
        
        return jsonify({
            'message': 'Blood request created',
            'request_id': blood_request.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create blood request failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create blood request'}), 500


@app.route('/api/donations', methods=['GET'])
def get_donations():
    """Get all donations (with pagination)."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        paginated = Donation.query.paginate(page=page, per_page=limit)
        
        return jsonify({
            'total': paginated.total,
            'page': page,
            'limit': limit,
            'data': [{
                'id': d.id,
                'donor_id': d.donor_id,
                'blood_type': d.blood_type,
                'quantity': d.quantity,
                'location': d.location,
                'donation_date': d.donation_date.isoformat()
            } for d in paginated.items]
        }), 200
        
    except Exception as e:
        logger.error(f"Get donations failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch donations'}), 500


# ======================== #
# Notification Routes
# ======================== #

@app.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    """Get user's notifications."""
    try:
        notifs = Notification.query.filter_by(user_id=current_user.id).order_by(
            Notification.created_at.desc()
        ).all()
        
        return jsonify([{
            'id': n.id,
            'message': n.message,
            'created_at': n.created_at.isoformat()
        } for n in notifs]), 200
        
    except Exception as e:
        logger.error(f"Get notifications failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch notifications'}), 500


# ======================== #
# Contact Route
# ======================== #

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Submit contact message."""
    try:
        data = request.get_json() or {}
        
        # Validation
        required = ['name', 'email', 'message']
        if not all(data.get(field) for field in required):
            return jsonify({'error': 'Name, email, and message are required'}), 400
        
        msg = ContactMessage(
            id=str(uuid.uuid4()),
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            subject=data.get('subject'),
            message=data['message'],
            created_at=datetime.datetime.utcnow()
        )
        
        db.session.add(msg)
        db.session.commit()
        
        logger.info(f"Contact message from {data['email']}")
        
        return jsonify({'message': 'Contact message received'}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Submit contact failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to submit contact message'}), 500


# ======================== #
# Admin Routes
# ======================== #

@app.route("/admin/pending-donors", methods=["GET"])
@token_required
def get_pending_donors(current_user):
    """Get pending donor approvals."""
    try:
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        paginated = Donor.query.filter_by(status="pending").paginate(
            page=page, per_page=limit
        )
        
        return jsonify({
            'total': paginated.total,
            'page': page,
            'data': [{
                'id': d.id,
                'user_id': d.user_id,
                'blood_type': d.blood_type,
                'is_available': d.is_available,
                'created_at': d.created_at.isoformat()
            } for d in paginated.items]
        }), 200
        
    except Exception as e:
        logger.error(f"Get pending donors failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch pending donors'}), 500


# ======================== #
# Frontend Pages
# ======================== #

@app.route('/')
def home():
    """Serve home page."""
    return render_template('index.html')


@app.route('/<path:name>.html')
def html_alias(name):
    """Serve any HTML file from templates."""
    try:
        return render_template(f'{name}.html')
    except Exception as e:
        logger.warning(f"Template not found: {name}")
        return "Not Found", 404


@app.route("/dashboard")
def dashboard():
    """Serve dashboard."""
    return render_template("dashboard.html")


@app.route('/about')
def about_page():
    """Serve about page."""
    return render_template('about.html')


@app.route("/adminPanel")
def admin_panel():
    """Serve admin panel."""
    return render_template("adminPanel.html")


@app.route("/recipient")
def recipient():
    """Serve recipient page."""
    try:
        if "user" not in session:
            return jsonify({"error": "User not logged in"}), 401
        
        user = session.get("user", {})
        return render_template(
            "Recipent.html",
            user=user,
            avatar_url=user.get("avatar", "/static/default-avatar.png")
        )
    except Exception as e:
        logger.error(f"Recipient page error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/protected")
def protected():
    """Protected route - requires session."""
    if "user" not in session:
        return jsonify({"error": "User not logged in"}), 401
    return jsonify({"message": f"Welcome {session['user']['name']}"})


@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Get blood inventory."""
    # This is a placeholder - should come from database
    inventory = [
        {"blood_group": "A+", "units": 10},
        {"blood_group": "B+", "units": 8},
        {"blood_group": "O+", "units": 15},
        {"blood_group": "AB+", "units": 5},
        {"blood_group": "A-", "units": 3},
        {"blood_group": "B-", "units": 2},
        {"blood_group": "O-", "units": 7},
        {"blood_group": "AB-", "units": 1},
    ]
    return jsonify(inventory), 200


# ======================== #
# Error Handlers
# ======================== #

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


# ======================== #
# Application Entry Point
# ======================== #

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=DEBUG
    )
