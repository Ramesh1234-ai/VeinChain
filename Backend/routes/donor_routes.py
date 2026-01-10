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