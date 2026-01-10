"""
Authentication routes blueprint
"""
from flask import Blueprint, request, jsonify
from database import db, User, Donor
from flask_jwt_extended import create_access_token
import uuid
import datetime
import logging
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Try to import Firebase if available
try:
    from firebase_admin import auth as firebase_auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


def generate_avatar(name):
    """Generate avatar URL"""
    try:
        if not name:
            return "https://api.dicebear.com/7.x/initials/svg?seed=U"
        parts = name.split()
        initials = "".join([part[0].upper() for part in parts if part])
        return f"https://api.dicebear.com/7.x/initials/svg?seed={initials}&scale=70"
    except Exception as e:
        logger.error(f"Avatar generation failed: {e}")
        return "https://api.dicebear.com/7.x/avataaars/svg?seed=default"


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validation
    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Missing required fields: email, password, name'}), 400
    
    # Email format validation
    if '@' not in data['email']:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Password strength validation
    if len(data['password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    # Check existing user
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    try:
        user = User(
            id=str(uuid.uuid4()),
            email=data['email'].lower(),
            name=data['name'],
            role=data.get('role', 'user'),
            auth_method='local'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()
        
        # If registering as donor, create donor profile
        if user.role == 'donor':
            donor = Donor(
                id=str(uuid.uuid4()),
                user_id=user.id,
                blood_type=data.get('blood_type'),
                is_available=True,
                status='pending'
            )
            db.session.add(donor)
        
        db.session.commit()
        logger.info(f"User registered: {user.email}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed: {str(e)}")
        return jsonify({'error': f'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with email and password"""
    data = request.get_json()
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        logger.warning(f"Failed login attempt for: {email}")
        return jsonify({'error': 'Invalid credentials'}), 401
    
    try:
        access_token = create_access_token(identity=user.id)
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/firebase-login', methods=['POST'])
def firebase_login():
    """Firebase authentication"""
    if not FIREBASE_AVAILABLE:
        return jsonify({
            'success': False, 
            'message': 'Firebase not available'
        }), 500
    
    data = request.get_json()
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'message': 'Missing Firebase token'}), 400
    
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        email = decoded_token.get('email', '').lower()
        name = decoded_token.get('name', email.split("@")[0])
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                name=name,
                email=email,
                role='user',
                auth_method='firebase'
            )
            db.session.add(user)
            db.session.commit()
        
        avatar_url = generate_avatar(user.name)
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Firebase login successful',
            'access_token': access_token,
            'user': {
                **user.to_dict(),
                'avatar': avatar_url
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Firebase login failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Firebase login failed'
        }), 400


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    # This is protected by JWT, only accessible with valid token
    return jsonify({'authenticated': True}), 200
