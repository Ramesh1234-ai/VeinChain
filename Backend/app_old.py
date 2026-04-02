import os, uuid, datetime, ssl, smtplib, logging
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
from email.message import EmailMessage
from firebase_admin import auth, credentials, initialize_app
import jwt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from database import db, User, Donor, BloodRequest, Donation, ContactMessage, Notification
from flask_session import Session
from datetime import timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------- #
# Load Environment Variables
# ------------------------- #
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

app = Flask(__name__)

# Firebase Admin SDK
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, "firebase_config.json")

print("Looking for Firebase config at:", cred_path)

# Make Firebase optional: if the service account file isn't present, continue
# but mark Firebase as disabled so routes depending on it can return helpful errors.
FIREBASE_ENABLED = False
try:
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        initialize_app(cred)
        FIREBASE_ENABLED = True
    else:
        print("Firebase config not found — continuing without Firebase.")
except Exception as e:
    print("Failed to initialize Firebase Admin SDK:", e)
    FIREBASE_ENABLED = False

# ------------------------- #
# Flask Setup
# ------------------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # Backend folder
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "Frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "..", "Frontend", "static")

app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR
)

# ✅ Use a consistent secret key (NOT random each time)
SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")  # change for production
app.secret_key = SECRET_KEY
app.config["SECRET_KEY"] = SECRET_KEY

# ✅ Proper session configuration
app.config["SESSION_TYPE"] = "filesystem"  # store sessions on disk
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)

# ✅ Critical for cookies to work in modern browsers
app.config["SESSION_COOKIE_SAMESITE"] = "None"  # allow cross-site usage
app.config["SESSION_COOKIE_SECURE"] = False     # set to True if using HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True    # prevents JS from stealing cookie

# ✅ CORS must allow credentials & correct origin
CORS(app, supports_credentials=True, origins=[
    "http://10.162.33.221:5500",  # your frontend (adjust port if needed)
    "http://localhost:5500"
])

# ✅ Initialize server-side session
Session(app)
jwt = JWTManager(app)
from config import Config

# Load configuration from Config class, allow environment override
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', app.config.get('SQLALCHEMY_DATABASE_URI')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = app.config.get(
    'SQLALCHEMY_TRACK_MODIFICATIONS', False
)

db.init_app(app)
with app.app_context():
    db.create_all()

# ------------------------- #
# Utility: Notifications
# ------------------------- #
def send_notification(user, message):
    try:
        notif = Notification(id=str(uuid.uuid4()), user_id=user.id, message=message)
        db.session.add(notif)
        db.session.commit()

        # Send Email
        msg = EmailMessage()
        msg['Subject'] = "Blood.Ninja Notification"
        msg['From'] = EMAIL_USER
        msg['To'] = user.email
        msg.set_content(message)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print("❌ Notification failed:", e)

# ------------------------- #
# Auth Decorator
# ------------------------- #
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if token:
            token = token.split(" ")[1]
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# ------------------------- #
# Auth Routes
# ------------------------- #
@app.route('/api/auth/register', methods=['POST'])
def register():
    username = request.form.get("username")
    avatar = request.form.get("avatar") or "default.png"

    # 🚨 normally you'd insert into DB / Firebase here
    user = {"username": username, "avatar": avatar}

    # ✅ Save in session
    session["user"] = user
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'message': 'Missing required fields'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    try:
        new_user = User(
            id=str(uuid.uuid4()),
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role=data.get('role', 'user'),
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.flush()

        if new_user.role == 'donor':
          donor = Donor(
        id=str(uuid.uuid4()),
        user_id=new_user.id,
        blood_type=data.get('blood_type'),
        is_available=True,
        status="pending"  # <-- wait for admin approval
        )
        db.session.add(donor)
        db.session.commit()
        send_notification(new_user, f"Welcome {new_user.name}! You are registered as {new_user.role}.")
        return jsonify({'message': 'User registered', 'user': {'id': new_user.id, 'email': new_user.email, 'name': new_user.name, 'role': new_user.role}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {e}'}), 500
#------------------------- #
# Login Route
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')  # or username
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401
# ------------------------- #
# Frontend Pages
# ------------------------- #
@app.route('/')
def home(): return render_template('index.html')
@app.route('/<path:name>.html')
def html_alias(name):
    try:
        return render_template(f'{name}.html')
    except:
        return ("Not Found", 404)
@app.route("/dashboard")
def dashboard():
    return render_template("DashBoard.html")
@app.route('/about')
def about_page(): return render_template('about.html')
@app.route("/adminPanel")
def adminPanel():
    return render_template("adminPanel.html")
@app.route("/recipient")
def recipient():
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
        return jsonify({"error": str(e)}), 500
#------------------------- #
@app.route('/verify_token', methods=['POST'])
def verify_token():
    data = request.get_json()
    token = data.get("token")

    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        email = decoded_token.get('email')
        return jsonify({"status": "success", "uid": uid, "email": email})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 401

# ------------------------- #
# Avatar Generation
# ------------------------- #
inventory = [
    {"blood_group": "A+", "units": 10},
    {"blood_group": "B+", "units": 8},
    {"blood_group": "O+", "units": 15},
    {"blood_group": "AB+", "units": 5},
]

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    return jsonify(inventory)

@app.route("/api/protected")
def protected():
    if "user" not in session:
        return jsonify({"error": "User not logged in"}), 401
    return jsonify({"message": f"Welcome {session['user']}"})
#-------------------------- #
def role_required(role):
    def wrapper(fn):
        @wraps(fn)  # ✅ preserves the original function name
        @jwt_required()
        def decorated_function(*args, **kwargs):
            identity = get_jwt_identity()
            if identity["role"] != role:
                return jsonify({"error": "Access forbidden"}), 403
            return fn(*args, **kwargs)
        return decorated_function
    return wrapper
@app.route("/donor/profile", methods=["GET"])
@role_required("donor")
def donor_profile():
    return jsonify({"message": "Welcome Donor! Here is your profile."})
@app.route("/recipient/requests", methods=["GET"])
@role_required("recipient")
def recipient_requests():
    return jsonify({"message": "Welcome Recipient! Here are your requests."})
# ------------------------- #
def generate_avatar(name):
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
#------------------------- #
# Get pending donors
@app.route("/admin/pending-donors", methods=["GET"])
@role_required("admin")
def get_pending_donors():
    donors = Donor.query.filter_by(status="pending").all()
    return jsonify([
        {
            "id": d.id,
            "user_id": d.user_id,
            "blood_type": d.blood_type,
            "is_available": d.is_available
        } for d in donors
    ]), 200

# Approve donor
@app.route("/admin/approve-donor/<donor_id>", methods=["PUT"])
@role_required("admin")
def approve_donor(donor_id):
    donor = Donor.query.filter_by(id=donor_id, status="pending").first()
    if not donor:
        return jsonify({"error": "Donor not found or already processed"}), 404
    donor.status = "approved"
    db.session.commit()
    user = User.query.get(donor.user_id)
    send_notification(user, f"Your donor registration has been approved!")
    return jsonify({"message": "Donor approved"}), 200

# Reject donor
@app.route("/admin/reject-donor/<donor_id>", methods=["DELETE"])
@role_required("admin")
def reject_donor(donor_id):
    donor = Donor.query.filter_by(id=donor_id, status="pending").first()
    if not donor:
        return jsonify({"error": "Donor not found or already processed"}), 404
    donor.status = "rejected"
    db.session.commit()
    user = User.query.get(donor.user_id)
    send_notification(user, f"Your donor registration has been rejected.")
    return jsonify({"message": "Donor rejected"}), 200
# Get pending blood requests
@app.route("/admin/pending-requests", methods=["GET"])
@role_required("admin")
def get_pending_requests():
    requests = BloodRequest.query.filter_by(status="pending").all()
    return jsonify([
        {
            "id": r.id,
            "requester_id": r.requester_id,
            "blood_type": r.blood_type,
            "quantity": r.quantity,
            "urgency": r.urgency,
            "hospital": r.hospital,
            "contact_number": r.contact_number,
            "notes": r.notes
        } for r in requests
    ]), 200
# Approve blood request
@app.route("/admin/approve-request/<request_id>", methods=["PUT"])
@role_required("admin")
def approve_request(request_id):
    br = BloodRequest.query.filter_by(id=request_id, status="pending").first()
    if not br:
        return jsonify({"error": "Request not found or already processed"}), 404
    br.status = "approved"
    db.session.commit()
    user = User.query.get(br.requester_id)
    send_notification(user, f"Your blood request has been approved!")
    return jsonify({"message": "Request approved"}), 200
# Reject blood request
@app.route("/admin/reject-request/<request_id>", methods=["DELETE"])
@role_required("admin")
def reject_request(request_id):
    br = BloodRequest.query.filter_by(id=request_id, status="pending").first()
    if not br:
        return jsonify({"error": "Request not found or already processed"}), 404
    br.status = "rejected"
    db.session.commit()
    user = User.query.get(br.requester_id)
    send_notification(user, f"Your blood request has been rejected.")
    return jsonify({"message": "Request rejected"}), 200
# ------------------------- #
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
