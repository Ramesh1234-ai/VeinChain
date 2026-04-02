# ======================== #
# Notification Routes
# ======================== #
@app.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    """Get user's notifications."""
    try:
        notifs = Notification.query.filter_by(user_id=current_user.id).order_by(
            Notification.created_at.desc()
        ).all()
        
        return jsonify([{
            'id': n.id,
            'message': n.message,
            'created_at': n.created_at.isoformat()
        } for n in notifs]), 200
        
    except Exception as e:
        logger.error(f"Get notifications failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch notifications'}), 500