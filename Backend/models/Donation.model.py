from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
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