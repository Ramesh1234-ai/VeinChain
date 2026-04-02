# Recipient Routes
@app.route('/api/recipients', methods=['GET'])
@role_required(['admin', 'recipient'])
def get_recipients():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    recipients = Recipient.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'recipients': [{
            'id': recipient.id,
            'name': recipient.name,
            'email': recipient.user.email,
            'phone': recipient.phone,
            'blood_group': recipient.blood_group,
            'required_units': recipient.required_units,
            'urgency': recipient.urgency,
            'hospital_name': recipient.hospital_name,
            'city': recipient.city,
            'state': recipient.state,
            'medical_condition': recipient.medical_condition,
            'created_at': recipient.created_at.isoformat()
        } for recipient in recipients.items],
        'total': recipients.total,
        'pages': recipients.pages,
        'current_page': page
    })

@app.route('/api/recipients', methods=['POST'])
@role_required(['admin', 'recipient'])
def create_recipient():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    required_fields = ['name', 'phone', 'blood_group', 'required_units', 'urgency', 'hospital_name', 'hospital_address', 'city', 'state']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    recipient = Recipient(
        user_id=current_user_id,
        name=data['name'],
        phone=data['phone'],
        blood_group=data['blood_group'],
        required_units=data['required_units'],
        urgency=data['urgency'],
        hospital_name=data['hospital_name'],
        hospital_address=data['hospital_address'],
        city=data['city'],
        state=data['state'],
        medical_condition=data.get('medical_condition', '')
    )
    
    db.session.add(recipient)
    db.session.commit()
    
    # Create a donation request
    donation_request = DonationRequest(
        recipient_id=recipient.id,
        status='pending'
    )
    db.session.add(donation_request)
    db.session.commit()
    
    return jsonify({
        'message': 'Recipient profile and donation request created successfully',
        'recipient': {
            'id': recipient.id,
            'name': recipient.name,
            'blood_group': recipient.blood_group,
            'urgency': recipient.urgency
        }
    }), 201