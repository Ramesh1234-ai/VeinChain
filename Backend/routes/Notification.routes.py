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
def send_notification(user, message):
    """Send notification to user via database and email."""
    try:
        # Save to database
        notif = Notification(
            id=str(uuid.uuid4()),
            user_id=user.id,
            message=message
        )
        db.session.add(notif)
        db.session.commit()
        
        # Send email if configured
        if not (EMAIL_USER and EMAIL_PASS):
            logger.warning("Email not configured, skipping email notification")
            return

        msg = EmailMessage()
        msg['Subject'] = "VeinChain Notification"
        msg['From'] = EMAIL_USER
        msg['To'] = user.email
        msg.set_content(message)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
            logger.info(f"Email notification sent to {user.email}")
    except Exception as e:
        logger.error(f"Notification failed: {e}", exc_info=True)

def token_required(f):
    """Decorator to require JWT token in Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            parts = token.split()
            if len(parts) != 2 or parts[0] != 'Bearer':
                return jsonify({'error': 'Invalid token format'}), 401
            
            token_str = parts[1]
            data = pyjwt.decode(token_str, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
                
        except pyjwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated
@app.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return jsonify([{'id': n.id, 'message': n.message, 'created_at': n.created_at.isoformat()} for n in notifs]), 200