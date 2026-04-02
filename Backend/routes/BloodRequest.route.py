@app.route('/api/blood-requests', methods=['POST'])
@token_required
def create_blood_request(current_user):
    """Create a new blood request."""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['blood_type', 'quantity', 'urgency', 'hospital', 'contact_number']
        if not all(data.get(field) for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        blood_request = BloodRequest(
            id=str(uuid.uuid4()),
            requester_id=current_user.id,
            blood_type=data['blood_type'],
            quantity=float(data['quantity']),
            urgency=data['urgency'],
            hospital=data['hospital'],
            contact_number=data['contact_number'],
            notes=data.get('notes', ''),
            request_date=datetime.datetime.utcnow(),
            status='pending'
        )
        
        db.session.add(blood_request)
        db.session.commit()
        
        send_notification(
            current_user,
            f"Your request for {blood_request.quantity} units of {blood_request.blood_type} has been submitted."
        )
        
        logger.info(f"Blood request created: {blood_request.id} by {current_user.email}")
        
        return jsonify({
            'message': 'Blood request created',
            'request_id': blood_request.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create blood request failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create blood request'}), 500