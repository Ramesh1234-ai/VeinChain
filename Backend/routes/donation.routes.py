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
@app.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return jsonify([{'id': n.id, 'message': n.message, 'created_at': n.created_at.isoformat()} for n in notifs]), 200
@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.get_json() or {}
    if not data.get('name') or not data.get('email') or not data.get('message'):
        return jsonify({'message': 'Name, email, and message required'}), 400
    msg = ContactMessage(
        id=str(uuid.uuid4()),
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        subject=data.get('subject'),
        message=data['message'],
        created_at=datetime.datetime.utcnow()
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'message': 'Contact message saved'}), 201