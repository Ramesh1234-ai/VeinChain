"""
VeinChain - Blood Donation Management System
Main Flask Application
"""
import os
import logging
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_session import Session
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
# Import database and config
from database import db
from config import get_config
from routes import auth_bp
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def generate_avatar(name):
    """Generate avatar URL using initials"""
    try:
        if not name:
            return "https://api.dicebear.com/7.x/initials/svg?seed=U"
        
        parts = name.split()
        initials = "".join([part[0].upper() for part in parts if part])
        return f"https://api.dicebear.com/7.x/initials/svg?seed={initials}&scale=70"
    except Exception as e:
        logger.error(f"Avatar generation failed: {e}")
        return "https://api.dicebear.com/7.x/avataaars/svg?seed=default"


def create_app(config=None):
    """Application factory pattern"""
    
    # Load configuration
    if config is None:
        config = get_config()
    
    # Create Flask app
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "Frontend", "templates")
    STATIC_DIR = os.path.join(BASE_DIR, "..", "Frontend", "static")
    
    app = Flask(
        __name__,
        template_folder=TEMPLATES_DIR,
        static_folder=STATIC_DIR
    )
    
    # Load config
    app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        app.config.get('SQLALCHEMY_DATABASE_URI')
    )
    
    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    Session(app)
    CORS(
        app, 
        supports_credentials=True, 
        origins=os.getenv('CORS_ORIGINS', 'http://localhost:5500').split(',')
    )
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Store generate_avatar in app context
    app.generate_avatar = generate_avatar
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
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
    
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/adminPanel')
    def admin_panel():
        return render_template('adminPanel.html')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info(f"App created with config: {config.__name__}")
    
    return app
# Create app instance for Gunicorn/Railway
app = create_app()
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)