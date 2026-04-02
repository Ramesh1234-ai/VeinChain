from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
db = SQLAlchemy()
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