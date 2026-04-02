# Donor Routes
@app.route('/api/donors', methods=['GET'])
@role_required(['admin', 'donor'])
def get_donors():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    blood_group = request.args.get('blood_group')
    city = request.args.get('city')
    
    query = Donor.query.filter_by(is_active=True)
    
    if blood_group:
        query = query.filter_by(blood_group=blood_group)
    if city:
        query = query.filter_by(city=city)
    
    donors = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'donors': [{
            'id': donor.id,
            'name': donor.name,
            'email': donor.user.email,
            'phone': donor.phone,
            'blood_group': donor.blood_group,
            'age': donor.age,
            'gender': donor.gender,
            'city': donor.city,
            'state': donor.state,
            'last_donation_date': donor.last_donation_date.isoformat() if donor.last_donation_date else None,
            'next_eligible_date': donor.next_eligible_date.isoformat() if donor.next_eligible_date else None,
            'is_eligible': donor.next_eligible_date <= datetime.now().date() if donor.next_eligible_date else True,
            'created_at': donor.created_at.isoformat()
        } for donor in donors.items],
        'total': donors.total,
        'pages': donors.pages,
        'current_page': page
    })

@app.route('/api/donors', methods=['POST'])
@role_required(['admin', 'donor'])
def create_donor():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Validate required fields
    required_fields = ['name', 'phone', 'blood_group', 'age', 'gender', 'address', 'city', 'state']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if donor profile already exists for this user
    existing_donor = Donor.query.filter_by(user_id=current_user_id).first()
    if existing_donor:
        return jsonify({'error': 'Donor profile already exists'}), 400
    
    # Create donor
    last_donation = None
    if data.get('last_donation_date'):
        last_donation = datetime.strptime(data['last_donation_date'], '%Y-%m-%d').date()
    
    donor = Donor(
        user_id=current_user_id,
        name=data['name'],
        phone=data['phone'],
        blood_group=data['blood_group'],
        age=data['age'],
        gender=data['gender'],
        address=data['address'],
        city=data['city'],
        state=data['state'],
        last_donation_date=last_donation,
        next_eligible_date=calculate_next_eligible_date(last_donation)
    )
    
    db.session.add(donor)
    db.session.commit()
    
    return jsonify({
        'message': 'Donor profile created successfully',
        'donor': {
            'id': donor.id,
            'name': donor.name,
            'blood_group': donor.blood_group,
            'city': donor.city,
            'state': donor.state
        }
    }), 201
@app.route('/api/donors/<int:donor_id>', methods=['PUT'])
@role_required(['admin', 'donor'])
def update_donor(donor_id):
    donor = Donor.query.get_or_404(donor_id)
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    # Check permissions
    if current_user.role != 'admin' and donor.user_id != current_user_id:
        return jsonify({'error': 'Insufficient permissions'}), 403
    data = request.get_json()
    # Update fields
    if 'name' in data:
        donor.name = data['name']
    if 'phone' in data:
        donor.phone = data['phone']
    if 'blood_group' in data:
        donor.blood_group = data['blood_group']
    if 'age' in data:
        donor.age = data['age']
    if 'gender' in data:
        donor.gender = data['gender']
    if 'address' in data:
        donor.address = data['address']
    if 'city' in data:
        donor.city = data['city']
    if 'state' in data:
        donor.state = data['state']
    if 'last_donation_date' in data:
        last_donation = datetime.strptime(data['last_donation_date'], '%Y-%m-%d').date()
        donor.last_donation_date = last_donation
        donor.next_eligible_date = calculate_next_eligible_date(last_donation)
    db.session.commit()
    return jsonify({'message': 'Donor updated successfully'})