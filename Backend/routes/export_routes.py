# Export Routes
@app.route('/api/export/donors', methods=['GET'])
@role_required(['admin'])
def export_donors():
    donors = Donor.query.filter_by(is_active=True).all()    
    export_data = {
        'export_date': datetime.now().isoformat(),
        'total_donors': len(donors),
        'donors': [{
            'id': donor.id,
            'name': donor.name,
            'email': donor.user.email,
            'phone': donor.phone,
            'blood_group': donor.blood_group,
            'age': donor.age,
            'gender': donor.gender,
            'address': donor.address,
            'city': donor.city,
            'state': donor.state,
            'last_donation_date': donor.last_donation_date.isoformat() if donor.last_donation_date else None,
            'next_eligible_date': donor.next_eligible_date.isoformat() if donor.next_eligible_date else None,
            'created_at': donor.created_at.isoformat()
        } for donor in donors]
    }
    return jsonify(export_data)
@app.route('/api/export/requests', methods=['GET'])
@role_required(['admin'])
def export_requests():
    requests = DonationRequest.query.all()
    
    export_data = {
        'export_date': datetime.now().isoformat(),
        'total_requests': len(requests),
        'requests': [{
            'id': req.id,
            'recipient_name': req.recipient.name,
            'recipient_blood_group': req.recipient.blood_group,
            'required_units': req.recipient.required_units,
            'urgency': req.recipient.urgency,
            'hospital_name': req.recipient.hospital_name,
            'city': req.recipient.city,
            'state': req.recipient.state,
            'donor_name': req.assigned_donor.name if req.assigned_donor else None,
            'donor_blood_group': req.assigned_donor.blood_group if req.assigned_donor else None,
            'status': req.status,
            'requested_date': req.requested_date.isoformat(),
            'fulfilled_date': req.fulfilled_date.isoformat() if req.fulfilled_date else None
        } for req in requests]
    }
    return jsonify(export_data)