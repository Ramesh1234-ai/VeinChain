from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
db = SQLAlchemy()
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