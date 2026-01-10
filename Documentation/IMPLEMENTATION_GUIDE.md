# VeinChain - Concrete Code Fixes & Implementation Guide

## Part 1: Quick Wins (Do These First - 2-4 Hours Each)

### Fix #1: Consolidate Database Models

**DELETE**: `Backend/models.py` (keep database.py version)  
**DELETE**: Donor/BloodRequest/Donation classes from `Backend/admin.py`

**REPLACE** `Backend/database.py` with:

```python
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Always use this field
    role = db.Column(db.String(20), default='user')
    auth_method = db.Column(db.String(50), default='local')  # 'local' or 'firebase'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    donations = db.relationship('Donation', backref='donor', foreign_keys='Donation.donor_id', lazy=True)
    blood_requests = db.relationship('BloodRequest', backref='requester', foreign_keys='BloodRequest.requester_id', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    donor_profile = db.relationship('Donor', backref='user', uselist=False, lazy=True)
    
    __table_args__ = (
        db.Index('idx_email', 'email'),
        db.Index('idx_role', 'role'),
    )
    
    def set_password(self, password):
        """Hash and set password"""
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = None
    
    def check_password(self, password):
        """Verify password against hash"""
        if not self.password_hash or not password:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'auth_method': self.auth_method,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Donor(db.Model):
    __tablename__ = 'donor'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    blood_type = db.Column(db.String(10), nullable=False)
    last_donation_date = db.Column(db.DateTime)
    medical_conditions = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_status', 'status'),
        db.Index('idx_user_id', 'user_id'),
    )

class BloodRequest(db.Model):
    __tablename__ = 'blood_request'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requester_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    blood_type = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    hospital = db.Column(db.String(200), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_status', 'status'),
        db.Index('idx_blood_type', 'blood_type'),
        db.Index('idx_requester_id', 'requester_id'),
    )

class Donation(db.Model):
    __tablename__ = 'donation'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    donor_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    donation_date = db.Column(db.DateTime, nullable=False)
    blood_type = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text)
    
    __table_args__ = (
        db.Index('idx_donor_id', 'donor_id'),
    )

class Notification(db.Model):
    __tablename__ = 'notification'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    __tablename__ = 'contact_message'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### Fix #2: Remove Exposed Credentials

**DELETE**: `Backend/.env` (Git will keep it, but next step removes from history)

**CREATE**: `Backend/.env.example`
```bash
# Email Configuration
EMAIL_USER=your_gmail@gmail.com
EMAIL_PASS=your_gmail_app_password_here

# Secret Keys
SECRET_KEY=generate_with_secrets.token_hex(32)
JWT_SECRET_KEY=generate_with_secrets.token_hex(32)

# Database
DATABASE_URL=sqlite:///blood_donation.db
# For production:
# DATABASE_URL=postgresql://user:password@host:5432/veinchain

# Environment
FLASK_ENV=development
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

# Port
PORT=5000
```

**ADD TO** `Backend/.gitignore`:
```
.env
*.env.local
firebase_config.json
instance/
__pycache__/
*.pyc
.DS_Store
.venv/
venv/
```

**REMOVE FROM GIT HISTORY**:
```bash
cd /path/to/VeinChain

# Option 1: Using git filter-branch
git filter-branch --tree-filter 'rm -f Backend/.env Backend/firebase_config.json' HEAD

# Option 2: Using BFG (faster)
git clone --mirror https://github.com/you/VeinChain VeinChain.git
bfg --delete-files .env --delete-files firebase_config.json VeinChain.git
cd VeinChain.git
git reflog expire --expire=now --all && git gc --prune=now --aggressive
cd ..
git push --mirror https://github.com/you/VeinChain
```

---

### Fix #3: Fix Login Routes (Delete Duplicate)

**IN** `Backend/app.py`, **DELETE** this entire block (around line 420-435):

```python
# DELETE THIS SECTION:
@app.route("/auth/login", methods=["POST"])
def adlogin():
    # verify username/password
    access_token = create_access_token(identity={"username": user.username, "role": user.role})
    
    # return token + optional redirect URL
    redirect_url = ""
    if user.role == "admin":
        redirect_url = "/admin/dashboard"
    elif user.role == "donor":
        redirect_url = "/donor/profile"
    elif user.role == "recipient":
        redirect_url = "/recipient/requests"
    
    return jsonify({"access_token": access_token, "redirect": redirect_url})
```

**KEEP** the first login route (around line 315):

```python
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):  # Now uses correct method
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401
```

---

### Fix #4: Implement Missing generate_avatar Function

**IN** `Backend/app.py`, **ADD** this function after imports (around line 100):

```python
# Avatar Generation
def generate_avatar(name):
    """
    Generate avatar URL using initials from user's name.
    Falls back to Dicebear API for avatar generation.
    """
    try:
        if not name:
            return "https://api.dicebear.com/7.x/initials/svg?seed=U"
        
        # Extract initials
        parts = name.split()
        initials = "".join([part[0].upper() for part in parts if part])
        
        # Use Dicebear API to generate avatar (no auth needed)
        return f"https://api.dicebear.com/7.x/initials/svg?seed={initials}&scale=70"
    except Exception as e:
        print(f"Avatar generation failed: {e}")
        return "https://api.dicebear.com/7.x/avataaars/svg?seed=default"
```

**THEN** update Firebase login to use it:

```python
# Line ~256 in firebase_login()
# Replace:
avatar_url = getattr(user, "avatar_url", None) or generate_avatar(user.name)

# Keep as is (now function exists)
```

---

### Fix #5: Update Config.py

**REPLACE** entire `Backend/config.py`:

```python
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-key-change-me-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///blood_donation.db'
    )
    
    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-only-key-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5500').split(',')
    
    # Email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

def get_config():
    """Get config based on environment"""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    
    return DevelopmentConfig
```

---

### Fix #6: Fix Frontend Hardcoded URLs

**IN** `Frontend/static/js/index2.js`, **REPLACE**:

```javascript
// OLD:
const res = await fetch("http://127.0.0.1:5000/api/auth/login", {

// NEW:
const res = await fetch("/api/auth/login", {
```

**IN** `Frontend/templates/Recipent.html`, **REPLACE ALL** occurrences:

```javascript
// OLD:
fetch("http://127.0.0.1:5000/api/auth/login", {
fetch("http://127.0.0.1:5000/api/auth/status", {
fetch("http://localhost:5000/api/protected", {

// NEW:
fetch("/api/auth/login", {
fetch("/api/auth/status", {
fetch("/api/protected", {
```

**CREATE** `Frontend/static/js/config.js`:

```javascript
/**
 * API Configuration
 * Automatically detects environment and sets correct API base URL
 */

const API_BASE_URL = (() => {
    const hostname = window.location.hostname;
    const port = window.location.port;
    const protocol = window.location.protocol;
    
    // Development environments
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return `${protocol}//${hostname}:5000`;
    }
    
    // Staging
    if (hostname === 'staging.yourdomain.com') {
        return 'https://api-staging.yourdomain.com';
    }
    
    // Production
    if (hostname === 'yourdomain.com' || hostname === 'www.yourdomain.com') {
        return 'https://api.yourdomain.com';
    }
    
    // Fallback to relative URLs
    return '';
})();

export { API_BASE_URL };
```

---

## Part 2: Fixing App Structure (4-6 Hours)

### Architecture: Single Flask App with Blueprints

**CREATE** `Backend/routes/__init__.py`:
```python
# Empty file to make routes a package
```

**CREATE** `Backend/routes/auth_routes.py`:
```python
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
```

**CREATE** `Backend/routes/donor_routes.py`:
```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db, User, Donor, Donation
import uuid
import datetime
import logging

logger = logging.getLogger(__name__)

donor_bp = Blueprint('donor', __name__)

@donor_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_donor_profile():
    """Get donor's profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    donor = Donor.query.filter_by(user_id=user_id).first()
    
    if not donor:
        return jsonify({'error': 'Donor profile not found'}), 404
    
    return jsonify({
        'user': user.to_dict(),
        'blood_type': donor.blood_type,
        'is_available': donor.is_available,
        'status': donor.status,
        'last_donation_date': donor.last_donation_date.isoformat() if donor.last_donation_date else None
    }), 200

@donor_bp.route('/donation', methods=['POST'])
@jwt_required()
def record_donation():
    """Record a new donation"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    donor = Donor.query.filter_by(user_id=user_id).first()
    
    if not donor or donor.status != 'approved':
        return jsonify({'error': 'Not approved as donor'}), 403
    
    data = request.get_json()
    
    # Validation
    if not data.get('blood_type') or not data.get('quantity') or not data.get('location'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Check eligibility (56 days since last donation)
        if donor.last_donation_date:
            days_since = (datetime.datetime.utcnow() - donor.last_donation_date).days
            if days_since < 56:
                return jsonify({'error': f'Can donate again after {56 - days_since} days'}), 409
        
        donation = Donation(
            id=str(uuid.uuid4()),
            donor_id=user_id,
            donation_date=datetime.datetime.utcnow(),
            blood_type=data['blood_type'],
            quantity=float(data['quantity']),
            location=data['location'],
            notes=data.get('notes', '')
        )
        
        donor.last_donation_date = datetime.datetime.utcnow()
        
        db.session.add(donation)
        db.session.commit()
        
        logger.info(f"Donation recorded for user: {user_id}")
        
        return jsonify({
            'message': 'Donation recorded successfully',
            'donation_id': donation.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Donation recording failed: {str(e)}")
        return jsonify({'error': f'Failed to record donation: {str(e)}'}), 500
```

**UPDATE** `Backend/app.py` to use blueprints:

```python
import os
import logging
from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_session import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and config
from database import db
from config import get_config

# Import blueprints
from routes.auth_routes import auth_bp
from routes.donor_routes import donor_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """Application factory"""
    
    # Load configuration
    if config is None:
        config = get_config()
    
    # Create Flask app
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), '..', 'Frontend', 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), '..', 'Frontend', 'static')
    )
    
    # Load config
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    Session(app)
    CORS(app, supports_credentials=True, origins=config.CORS_ORIGINS)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(donor_bp, url_prefix='/api/donor')
    
    # Frontend routes
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/login')
    def login_page():
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        return render_template('register.html')
    
    logger.info(f"App created with config: {config.__name__}")
    
    return app

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
```

---

## Part 3: Testing Your Fixes

### Test Checklist

```bash
# 1. Test imports
python -c "from database import db, User, Donor; print('Models OK')"

# 2. Test Flask app creation
python -c "from app import create_app; app = create_app(); print('App OK')"

# 3. Run database creation
python
>>> from app import create_app
>>> app = create_app()
>>> with app.app_context():
...     from database import db
...     db.create_all()
...     print("Database initialized")

# 4. Test API endpoints with curl
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'

# 5. Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

---

## Part 4: Deployment File Updates

### Updated requirements.txt

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Cors==4.0.0
Flask-JWT-Extended==4.5.3
Flask-Session==0.5.0
Flask-Migrate==4.0.5
python-dotenv==1.0.0
firebase-admin==6.2.0
Werkzeug==3.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

### Updated Procfile

```plaintext
web: gunicorn --workers 4 --worker-class sync --timeout 60 --bind 0.0.0.0:$PORT app:app
release: flask db upgrade
```

### Updated runtime.txt

```plaintext
python-3.12.4
```

---

## Validation Checklist (Before Deployment)

- [ ] All credentials removed from source code
- [ ] .env file added to .gitignore
- [ ] Firebase config file added to .gitignore
- [ ] No hardcoded URLs in JavaScript
- [ ] Database models consolidated
- [ ] Login endpoint working (test with curl)
- [ ] Register endpoint working
- [ ] Firebase login optional (graceful fallback)
- [ ] Logging configured
- [ ] CORS headers correct
- [ ] All imports resolve without errors
- [ ] Database migrations created
- [ ] Environment variables documented in .env.example
- [ ] README.md updated with setup instructions
- [ ] Tests pass locally

---

## Quick Reference: Files to Create/Delete

### CREATE
- [ ] `Backend/.env.example`
- [ ] `Backend/routes/__init__.py`
- [ ] `Backend/routes/auth_routes.py`
- [ ] `Backend/routes/donor_routes.py`
- [ ] `Frontend/static/js/config.js`

### UPDATE
- [ ] `Backend/app.py` (consolidate)
- [ ] `Backend/database.py` (unified models)
- [ ] `Backend/config.py`
- [ ] `Backend/requirements.txt`
- [ ] `Backend/Procfile`
- `Frontend/static/js/index2.js`
- [ ] `Frontend/templates/Recipent.html`
- [ ] `.gitignore`

### DELETE
- [ ] `Backend/models.py`
- [ ] `Backend/admin.py`
- [ ] `Backend/dashboard.py`
- [ ] `Backend/.env` (after migration)

---

This completes the concrete implementation guide. Follow Part 1-4 in order!
