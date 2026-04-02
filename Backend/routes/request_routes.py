# Donation Request Routes
@app.route('/api/requests', methods=['GET'])
@role_required(['admin'])
def get_donation_requests():
    requests = DonationRequest.query.all()
    
    return jsonify({
        'requests': [{
            'id': req.id,
            'recipient': {
                'id': req.recipient.id,
                'name': req.recipient.name,
                'blood_group': req.recipient.blood_group,
                'required_units': req.recipient.required_units,
                'urgency': req.recipient.urgency,
                'hospital_name': req.recipient.hospital_name,
                'city': req.recipient.city,
                'state': req.recipient.state
            },
            'donor': {
                'id': req.assigned_donor.id,
                'name': req.assigned_donor.name,
                'blood_group': req.assigned_donor.blood_group,
                'city': req.assigned_donor.city
            } if req.assigned_donor else None,
            'status': req.status,
            'requested_date': req.requested_date.isoformat(),
            'fulfilled_date': req.fulfilled_date.isoformat() if req.fulfilled_date else None,
            'notes': req.notes
        } for req in requests]
    })

@app.route('/api/requests/<int:request_id>/match', methods=['POST'])
@role_required(['admin'])
def match_donor_to_request(request_id):
    donation_request = DonationRequest.query.get_or_404(request_id)
    
    if donation_request.status != 'pending':
        return jsonify({'error': 'Request is not pending'}), 400
    
    # Find compatible donors
    compatible_donors = find_compatible_donors(
        donation_request.recipient.blood_group,
        donation_request.recipient.city,
        donation_request.recipient.state
    )
    
    if not compatible_donors:
        return jsonify({'error': 'No compatible donors found'}), 404
    
    return jsonify({
        'compatible_donors': [{
            'id': donor.id,
            'name': donor.name,
            'blood_group': donor.blood_group,
            'city': donor.city,
            'phone': donor.phone,
            'last_donation_date': donor.last_donation_date.isoformat() if donor.last_donation_date else None,
            'next_eligible_date': donor.next_eligible_date.isoformat() if donor.next_eligible_date else None
        } for donor in compatible_donors]
    })

@app.route('/api/requests/<int:request_id>/assign', methods=['PUT'])
@role_required(['admin'])
def assign_donor_to_request(request_id):
    data = request.get_json()
    donor_id = data.get('donor_id')
    
    if not donor_id:
        return jsonify({'error': 'donor_id is required'}), 400
    
    donation_request = DonationRequest.query.get_or_404(request_id)
    donor = Donor.query.get_or_404(donor_id)
    
    donation_request.donor_id = donor_id
    donation_request.status = 'matched'
    
    db.session.commit()
    
    return jsonify({'message': 'Donor assigned successfully'})

@app.route('/api/requests/<int:request_id>/fulfill', methods=['PUT'])
@role_required(['admin'])
def fulfill_request(request_id):
    donation_request = DonationRequest.query.get_or_404(request_id)
    
    if donation_request.status != 'matched':
        return jsonify({'error': 'Request must be matched before fulfilling'}), 400
    
    donation_request.status = 'fulfilled'
    donation_request.fulfilled_date = datetime.utcnow()
    
    # Update donor's last donation date
    if donation_request.assigned_donor:
        today = datetime.now().date()
        donation_request.assigned_donor.last_donation_date = today
        donation_request.assigned_donor.next_eligible_date = calculate_next_eligible_date(today)
    
    db.session.commit()
    
    return jsonify({'message': 'Request fulfilled successfully'})