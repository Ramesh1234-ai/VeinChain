# ------------------------- #
# Donations & Blood Requests
# ------------------------- #
@app.route('/api/donations', methods=['POST'])
@token_required
def create_donation(current_user):
    if current_user.role != 'donor':
        return jsonify({'message': 'Not authorized'}), 403
    data = request.get_json()
    new_donation = Donation(
        id=str(uuid.uuid4()),
        donor_id=current_user.id,
        donation_date=datetime.datetime.now(),
        blood_type=data['blood_type'],
        quantity=data['quantity'],
        location=data['location'],
        notes=data.get('notes', '')
    )
    donor = Donor.query.filter_by(user_id=current_user.id).first()
    if donor:
        donor.last_donation_date = datetime.datetime.now()
    db.session.add(new_donation)
    db.session.commit()
    send_notification(current_user, f"Thanks {current_user.name}! Your donation of {new_donation.quantity}ml {new_donation.blood_type} has been recorded.")
    return jsonify({'message': 'Donation recorded'}), 201

@app.route('/api/blood-requests', methods=['POST'])
@token_required
def create_blood_request(current_user):
    data = request.get_json()
    new_request = BloodRequest(
        id=str(uuid.uuid4()),
        requester_id=current_user.id,
        blood_type=data['blood_type'],
        quantity=data['quantity'],
        urgency=data['urgency'],
        hospital=data['hospital'],
        contact_number=data['contact_number'],
        notes=data.get('notes', ''),
        request_date=datetime.datetime.now(),
        status='pending'
    )
    db.session.add(new_request)
    db.session.commit()
    send_notification(current_user, f"Your request for {new_request.quantity} units of {new_request.blood_type} has been submitted.")
    return jsonify({'message': 'Blood request created'}), 201
# ======================== #
# Donation Routes
# ======================== #
@app.route('/api/donations', methods=['GET'])
def get_donations():
    """Get all donations (with pagination)."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        paginated = Donation.query.paginate(page=page, per_page=limit)
        
        return jsonify({
            'total': paginated.total,
            'page': page,
            'limit': limit,
            'data': [{
                'id': d.id,
                'donor_id': d.donor_id,
                'blood_type': d.blood_type,
                'quantity': d.quantity,
                'location': d.location,
                'donation_date': d.donation_date.isoformat()
            } for d in paginated.items]
        }), 200
        
    except Exception as e:
        logger.error(f"Get donations failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch donations'}), 500
