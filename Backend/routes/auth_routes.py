from flask import Blueprint, request, jsonify
from database import db, User
from flask_jwt_extended import create_access_token
import uuid
import datetime
import os
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validation
    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check existing user
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Password strength validation
    if len(data['password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    try:
        user = User(
            id=str(uuid.uuid4()),
            email=data['email'],
            name=data['name'],
            role=data.get('role', 'user'),
            auth_method='local'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User registered: {user.email}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

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

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    # This is handled by JWT, only accessible with valid token
    return jsonify({'authenticated': True}), 200
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