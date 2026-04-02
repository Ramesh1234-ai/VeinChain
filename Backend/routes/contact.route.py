# ======================== #
# Contact Route
# ======================== #
@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Submit contact message."""
    try:
        data = request.get_json() or {}
        # Validation
        required = ['name', 'email', 'message']
        if not all(data.get(field) for field in required):
            return jsonify({'error': 'Name, email, and message are required'}), 400
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
        logger.info(f"Contact message from {data['email']}")
        return jsonify({'message': 'Contact message received'}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Submit contact failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to submit contact message'}), 500