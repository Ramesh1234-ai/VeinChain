def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or user.role not in required_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
def calculate_next_eligible_date(last_donation_date):
    if last_donation_date:
        return last_donation_date + timedelta(days=90)  # 3 months gap
    return datetime.now().date()
def find_compatible_donors(blood_group, city, state):
    # Find donors who can donate to this blood group
    compatible_donors = []
    for donor_bg, can_donate_to in BLOOD_COMPATIBILITY.items():
        if blood_group in can_donate_to:
            # Find eligible donors
            today = datetime.now().date()
            donors = Donor.query.filter(
                Donor.blood_group == donor_bg,
                Donor.city == city,
                Donor.is_active == True,
                db.or_(
                    Donor.next_eligible_date == None,
                    Donor.next_eligible_date <= today
                )
            ).all()
            compatible_donors.extend(donors)
    return compatible_donors