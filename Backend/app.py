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
from middleware  import token_required
# Firebase (optional)
try:
    from firebase_admin import auth, credentials, initialize_app
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

import jwt as pyjwt
# Import models
from models import db, User, Donor, BloodRequest, Donation, ContactMessage, Notification
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
#Importing models from model folder
db=SQLAlchemy()
db.init_app(app)
# Initialize extensions
Session(app)
JWTManager(app)
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
# Application Entry Point
# ======================== #
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=DEBUG
    )
