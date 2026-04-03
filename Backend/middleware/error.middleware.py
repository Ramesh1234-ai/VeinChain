@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
@app.route("/_ping")
def _ping():
    return "ok"
if __name__ == '__main__':
    # Initialize database on startup
    if init_database():
        logger.info("Starting Blood Donation Management System API")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        logger.error("Failed to initialize database. Exiting.")
        exit(1)