# VeinChain - Quick Start Guide for Developers

## What Was Fixed?

All issues from the code review have been addressed:

### ✅ Critical Security Fixes
- Removed exposed Firebase credentials from JavaScript files
- Created `.env.example` with template values (no credentials)
- Updated `.gitignore` to prevent accidental credential commits
- Implemented proper environment variable handling
- Fixed password hashing field naming inconsistencies

### ✅ Code Architecture Fixes
- Consolidated 3 separate Flask app instances into single `app.py`
- Merged duplicate login routes
- Removed `admin.py` and `dashboard.py` (functionality merged)
- Unified database models in single `database.py`
- Fixed undefined `generate_avatar()` function

### ✅ Configuration Improvements
- Updated `Procfile` to use correct app entry point
- Created `config.py` with environment-based settings
- Added `render.yaml` for Render deployment
- Configured CORS from environment variables
- Proper logging throughout application

### ✅ Frontend Improvements
- Removed hardcoded localhost URLs (now use relative URLs)
- Firebase credentials now use environment-based config
- Updated to use `/api/` relative endpoints

---

## Local Development Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/VeinChain.git
cd VeinChain

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r Backend/requirements.txt
```

### 2. Configure Environment

```bash
# Create .env file (copy from .env.example)
cp Backend/.env.example Backend/.env

# Edit .env with your local values
nano Backend/.env
# Or use your editor:
# - EMAIL_USER: your Gmail
# - EMAIL_PASS: Gmail App Password
# - SECRET_KEY: keep as is for dev
# - JWT_SECRET_KEY: keep as is for dev
```

### 3. Run the Application

```bash
# Navigate to Backend
cd Backend

# Run Flask app
python app.py

# You should see:
# * Running on http://127.0.0.1:5000
```

### 4. Start Frontend

In a new terminal:

```bash
cd Frontend

# Start a simple HTTP server
python -m http.server 5500

# Navigate to http://localhost:5500
```

---

## Testing Endpoints

### Using curl

```bash
# Test home page
curl http://localhost:5000/

# Get blood inventory
curl http://localhost:5000/api/inventory

# Register new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "donor@example.com",
    "password": "Test@123",
    "name": "John Donor",
    "role": "donor"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "donor@example.com",
    "password": "Test@123"
  }'

# Use the returned access_token for protected endpoints
TOKEN="your_token_here"
curl http://localhost:5000/api/protected \
  -H "Authorization: Bearer $TOKEN"
```

### Using Postman

1. Import this collection (optional)
2. Create requests for each endpoint
3. Use variables for tokens and base URL
4. Test all auth flows

---

## Project Structure

```
VeinChain/
├── Backend/
│   ├── app.py              # Main Flask application (SINGLE ENTRY POINT)
│   ├── database.py         # Database models (Unified)
│   ├── config.py           # Configuration (environment-based)
│   ├── requirements.txt    # Python dependencies
│   ├── Procfile            # Deployment entry point
│   ├── .env.example        # Environment template (NO CREDENTIALS)
│   ├── .env.production     # Production env template
│   └── routes/             # API routes (optional - for Phase 2 refactoring)
│
├── Frontend/
│   ├── static/
│   │   ├── css/            # Stylesheets
│   │   ├── js/
│   │   │   ├── config.js   # API configuration
│   │   │   ├── index.js    # Firebase auth (credentials removed)
│   │   │   └── index2.js   # Login form (credentials removed)
│   │   └── images/         # Images
│   └── templates/          # HTML pages
│
├── render.yaml             # Render deployment config
├── RENDER_DEPLOYMENT.md    # Render deployment guide
├── DEPLOYMENT_CHECKLIST.md # Full deployment checklist
├── CODE_REVIEW.md          # Original code review
└── README.md               # Main documentation
```

---

## Important Files to Know

| File | Purpose | Modified? |
|------|---------|-----------|
| `Backend/app.py` | Main Flask app - REWRITTEN | ✓ Yes |
| `Backend/database.py` | Database models | ✓ Updated |
| `Backend/config.py` | Settings | ✓ Updated |
| `Backend/.env.example` | Env template | ✓ Created |
| `Backend/Procfile` | Deployment config | ✓ Fixed |
| `Frontend/static/js/index.js` | Firebase login | ✓ Fixed |
| `Frontend/static/js/index2.js` | Regular login | ✓ Fixed |
| `render.yaml` | Render config | ✓ Created |
| `RENDER_DEPLOYMENT.md` | Deploy guide | ✓ Created |

---

## Key Environment Variables

```bash
# Required
FLASK_ENV=development
SECRET_KEY=dev-key
JWT_SECRET_KEY=dev-key
EMAIL_USER=your_gmail@gmail.com
EMAIL_PASS=your_app_password

# Optional
DATABASE_URL=sqlite:///blood_donation.db  # or PostgreSQL
CORS_ORIGINS=http://localhost:5500
DEBUG=True
PORT=5000
```

---

## Common Development Tasks

### Add a New Endpoint

```python
# In Backend/app.py

@app.route('/api/myfeature', methods=['GET'])
@token_required  # Add this if endpoint needs auth
def my_feature(current_user):  # Add current_user if using @token_required
    """Short description."""
    try:
        # Your code here
        return jsonify({'result': 'data'}), 200
    except Exception as e:
        logger.error(f"My feature failed: {e}", exc_info=True)
        return jsonify({'error': 'Something went wrong'}), 500
```

### Add a New Database Model

```python
# In Backend/database.py

class MyModel(db.Model):
    __tablename__ = 'my_model'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('ParentModel', backref='children', lazy=True)
```

### Run Database Initialization

```bash
# From Backend directory
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✓ Database initialized')
"
```

### Check Database

```bash
# Using SQLite
sqlite3 blood_donation.db
> .schema user
> SELECT COUNT(*) FROM user;
> .quit
```

---

## Debugging Tips

### Enable Debug Mode

```python
# In Backend/app.py, near the end:
if __name__ == '__main__':
    app.run(debug=True)  # Auto-reload on file changes
```

### View Logs

```python
# Already configured - look at console output
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### Test Database Queries

```bash
python -c "
from Backend.app import app, db
from Backend.database import User

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f'{user.email}: {user.role}')
"
```

---

## Next Steps (Phase 2)

- [ ] Add rate limiting to auth endpoints
- [ ] Add input validation and sanitization
- [ ] Implement proper error responses
- [ ] Add API documentation (Swagger)
- [ ] Set up automated testing
- [ ] Implement blood compatibility matching
- [ ] Add donation eligibility checks
- [ ] Create admin dashboard features
- [ ] Add email notification system
- [ ] Set up monitoring and alerts

---

## Deployment

When ready to deploy to Render:

```bash
# 1. Make sure everything works locally
python app.py
# Test in browser at http://localhost:5500

# 2. Commit changes
git add -A
git commit -m "Your commit message"
git push origin main

# 3. Render automatically deploys
# Watch logs in Render dashboard

# 4. Test production URL
curl https://yourdomain.com/api/inventory
```

See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for detailed instructions.

---

## Troubleshooting

### "Module not found" errors
```bash
# Make sure venv is activated
# Reinstall requirements
pip install -r Backend/requirements.txt
```

### Port already in use
```bash
# Use different port
python app.py  # Edit app.py to change port
# Or kill process:
# Windows: netstat -ano | findstr :5000
# macOS/Linux: lsof -i :5000 | kill -9 <PID>
```

### Database connection errors
```bash
# Remove old database and recreate
rm Backend/blood_donation.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### CORS errors
```python
# Check CORS_ORIGINS in .env
# Should include your frontend URL
# Example: CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

---

## Support

- **Code Review**: See [CODE_REVIEW.md](./CODE_REVIEW.md)
- **Deployment Guide**: See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)
- **Checklist**: See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- **Issues**: Check GitHub Issues

---

**Happy Coding! 🚀**
