from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
from . import db
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