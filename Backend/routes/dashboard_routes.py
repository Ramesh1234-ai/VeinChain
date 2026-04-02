# Dashboard & Statistics
@app.route('/api/dashboard/stats', methods=['GET'])
@role_required(['admin'])
def get_dashboard_stats():
    today = datetime.now().date()
    
    # Total counts
    total_donors = Donor.query.filter_by(is_active=True).count()
    total_recipients = Recipient.query.count()
    
    # Eligible donors (can donate today)
    eligible_donors = Donor.query.filter(
        Donor.is_active == True,
        db.or_(
            Donor.next_eligible_date == None,
            Donor.next_eligible_date <= today
        )
    ).count()
    
    # Request statistics
    pending_requests = DonationRequest.query.filter_by(status='pending').count()
    matched_requests = DonationRequest.query.filter_by(status='matched').count()
    fulfilled_requests = DonationRequest.query.filter_by(status='fulfilled').count()
    
    # Blood group distribution
    blood_groups = db.session.query(Donor.blood_group, db.func.count(Donor.id)).group_by(Donor.blood_group).all()
    
    return jsonify({
        'total_donors': total_donors,
        'total_recipients': total_recipients,
        'eligible_donors': eligible_donors,
        'active_donors': eligible_donors,
        'pending_requests': pending_requests,
        'matched_requests': matched_requests,
        'fulfilled_requests': fulfilled_requests,
        'blood_group_distribution': [{'blood_group': bg, 'count': count} for bg, count in blood_groups]
    })