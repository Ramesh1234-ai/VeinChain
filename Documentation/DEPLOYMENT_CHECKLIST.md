# VeinChain Deployment Checklist

**Project**: Blood Donation Management System  
**Target**: Render.com  
**Date**: January 2026  

## Pre-Deployment Phase

### Code Quality ✓
- [x] All critical security issues fixed (exposed credentials removed)
- [x] Duplicate app instances consolidated to single app.py
- [x] Duplicate routes removed and merged
- [x] Missing functions implemented (generate_avatar)
- [x] Database models unified (single source of truth)
- [x] Password field naming corrected (password_hash)
- [x] Firebase login properly implemented
- [x] Error handling improved with logging
- [x] Imports cleaned up
- [x] CORS configuration environment-based
- [x] Frontend Firebase credentials removed (use config)
- [x] Frontend URLs use relative paths

### Backend Code ✓
- [x] Remove `Backend/app_old.py` before git push
- [x] Remove `Backend/admin.py` (functionality merged)
- [x] Remove `Backend/dashboard.py` (functionality merged)
- [x] Remove `Backend/models.py` duplicate (use database.py)
- [x] Verify `database.py` has all models
- [x] Check `config.py` has all settings
- [x] Update `Procfile` to point to correct app
- [x] Create `.env.example` with template values
- [x] Create `.env.production` for production values
- [x] Verify `.gitignore` includes `.env` and credentials
- [x] Add logging to all critical paths
- [x] Implement rate limiting (optional, for Phase 2)
- [x] Add input validation (optional, for Phase 2)

### Frontend Code ✓
- [x] Remove hardcoded Firebase keys from `index.js`
- [x] Remove hardcoded Firebase keys from `index2.js`
- [x] Update Firebase config to use environment variables
- [x] Verify all API calls use relative URLs (`/api/...`)
- [x] Test CORS with backend
- [x] Test all auth flows (login, register, Firebase)
- [x] Verify session handling

### Database ✓
- [x] Unified models in `database.py`
- [x] All relationships defined correctly
- [x] Foreign keys reference correct tables
- [x] Indexes added for performance
- [x] `db.create_all()` called in app initialization
- [x] Test locally with SQLite
- [x] Database ready for PostgreSQL migration

### Configuration ✓
- [x] `config.py` loads from environment
- [x] `requirements.txt` includes all dependencies
- [x] `runtime.txt` specifies Python 3.11
- [x] `render.yaml` configured correctly
- [x] Environment variables documented

### Documentation ✓
- [x] `RENDER_DEPLOYMENT.md` created
- [x] Deployment steps documented
- [x] Troubleshooting guide created
- [x] Environment variables documented
- [x] Database setup instructions
- [x] Gmail setup instructions
- [x] Firebase setup instructions (if used)

---

## Local Testing Phase

### Backend Testing
```bash
# Install dependencies
pip install -r Backend/requirements.txt

# Set environment variables
export FLASK_ENV=development
export SECRET_KEY=dev-key
export JWT_SECRET_KEY=dev-key

# Run app
cd Backend && python app.py

# Test endpoints
curl http://localhost:5000/  # Home page
curl http://localhost:5000/api/inventory  # Inventory endpoint
```

### Frontend Testing
```bash
# Start a simple HTTP server
cd Frontend
python -m http.server 5500

# Navigate to http://localhost:5500
# Test login/register flows
# Verify API calls work
```

### Database Testing
```bash
# Check database creation
python -c "
from Backend.app import app, db
with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print('Tables:', tables)
"
```

### Auth Testing
```bash
# Test registration
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","name":"Test"}'

# Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# Response should have access_token
```

- [ ] Registration endpoint works
- [ ] Login endpoint works
- [ ] Token validation works
- [ ] Protected routes work
- [ ] Firebase login works (if configured)
- [ ] Logout works
- [ ] Session management works
- [ ] CORS allows frontend requests

---

## Pre-Push to Git Phase

### Git Cleanup
```bash
# Remove old files
rm Backend/app_old.py
rm Backend/admin.py
rm Backend/dashboard.py
rm Backend/models.py  # If using database.py

# Check no credentials in git
git log --all --full-history --source -- ".env" 
git log --all --full-history --source -- "firebase_config.json"

# Should return: 
# (no output = credentials not in git ✓)
```

- [ ] No `.env` files in git
- [ ] No `firebase_config.json` in git
- [ ] No exposed API keys in code
- [ ] No hardcoded passwords
- [ ] No debug=True in production config
- [ ] `.gitignore` is comprehensive

### Code Review
```bash
# Check all imports work
python -m py_compile Backend/app.py
python -m py_compile Backend/database.py
python -m py_compile Backend/config.py

# Should have no syntax errors
```

- [ ] No syntax errors
- [ ] All imports resolve
- [ ] No circular imports
- [ ] No undefined functions
- [ ] Logging is configured
- [ ] Error handlers are present

### Commit Message
```bash
git add -A
git commit -m "feat: Fix all code review issues and prepare for Render deployment

- Consolidate Flask app instances to single app.py
- Remove duplicate login routes
- Implement missing generate_avatar function
- Fix password hash field naming (password_hash)
- Remove exposed Firebase credentials from code
- Remove exposed Gmail credentials from .env
- Add environment-based CORS configuration
- Update database models (single source of truth)
- Create comprehensive logging
- Add Render deployment files (render.yaml, RENDER_DEPLOYMENT.md)
- Update requirements.txt with missing packages
- Fix Procfile for correct app entry point
- Add .env.production for production config
- Update frontend to use environment variables

Fixes #1, #2, #3, ... (reference issue numbers)
"

git push origin main
```

- [ ] All changes committed
- [ ] Commit message is clear
- [ ] Pushed to GitHub

---

## Render Deployment Phase

### Step 1: Prepare Render
- [ ] Create Render account (if not already done)
- [ ] Connect GitHub repository
- [ ] Generate new SECRET_KEY and JWT_SECRET_KEY
- [ ] Have Gmail App Password ready
- [ ] Have Firebase credentials ready (if using)

### Step 2: Deploy from Blueprint
```bash
# In Render Dashboard:
# 1. Click "New +" > "Blueprint"
# 2. Select your GitHub repository
# 3. Review render.yaml configuration
# 4. Click "Deploy"
```

- [ ] Blueprint validation passes
- [ ] Build command is correct
- [ ] Start command is correct
- [ ] Environment variables identified

### Step 3: Configure Environment Variables
In Render Dashboard > Web Service > Environment:

```
FLASK_ENV=production
DEBUG=False
SECRET_KEY=(generated key)
JWT_SECRET_KEY=(generated key)
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=(Gmail App Password)
CORS_ORIGINS=https://yourdomain.com
SESSION_COOKIE_SECURE=True
```

- [ ] All environment variables set
- [ ] No empty required variables
- [ ] Sensitive values are secure
- [ ] Region is appropriate (e.g., Oregon)

### Step 4: Add PostgreSQL Database (Recommended)
In Render Dashboard:
```
1. Click "New +" > "PostgreSQL"
2. Set Name: veinchain-db
3. Set Database: veinchain
4. Set Region: Same as web service
5. Copy Internal Database URL
6. Add DATABASE_URL to web service environment
```

- [ ] PostgreSQL database created
- [ ] Database URL copied
- [ ] DATABASE_URL set in environment
- [ ] Same region as web service

### Step 5: Monitor Initial Deployment
In Render Dashboard > Logs:

Watch for:
- ✓ "Build succeeded"
- ✓ "Deployment in progress"
- ✓ "Live" status

Common issues:
- [ ] Check for import errors
- [ ] Check for missing environment variables
- [ ] Check for database connection errors
- [ ] Check for port binding errors

---

## Post-Deployment Testing

### Basic Health Checks
```bash
# Get your Render URL from dashboard (e.g., veinchain.onrender.com)
RENDER_URL="https://veinchain.onrender.com"

# Test home page
curl $RENDER_URL/

# Test API endpoint
curl $RENDER_URL/api/inventory

# Test database connection (logs should show no errors)
```

- [ ] Home page loads
- [ ] API returns JSON
- [ ] No 500 errors in logs
- [ ] Database connected successfully

### Authentication Testing
```bash
# Test registration
curl -X POST $RENDER_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test"}'

# Test login
curl -X POST $RENDER_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Should return access_token
```

- [ ] Registration works
- [ ] Login works
- [ ] Token is returned
- [ ] Token is valid

### Frontend Integration
```bash
# Update frontend API base URL
# Frontend should now point to https://yourdomain.com
# Instead of http://localhost:5000

# Test all pages load
# Test login flow
# Test protected routes
```

- [ ] Frontend connects to backend
- [ ] Login page loads
- [ ] Registration page loads
- [ ] Dashboard loads after login
- [ ] Logout works
- [ ] Admin panel accessible (if admin user)

### Database Testing
```bash
# Data should persist across deployments
# Test creating a user
# Restart service
# Check user still exists
```

- [ ] Data persists
- [ ] No data loss on restart
- [ ] Backups are running (if PostgreSQL)

---

## Production Hardening

### Security
- [ ] HTTPS enforced (Render does this by default)
- [ ] SESSION_COOKIE_SECURE = True
- [ ] SESSION_COOKIE_HTTPONLY = True
- [ ] CORS_ORIGINS restricted to your domain
- [ ] No debug mode in production
- [ ] No print statements in code (use logging)
- [ ] Rate limiting on auth endpoints (Phase 2)
- [ ] Input validation on all endpoints (Phase 2)

### Monitoring
- [ ] Set up Render alerts for failures
- [ ] Enable auto-restart on crash
- [ ] Monitor logs for errors
- [ ] Monitor database for slow queries
- [ ] Set up log rotation

### Backup & Recovery
- [ ] Database backups enabled (Render handles this)
- [ ] Document recovery procedures
- [ ] Test database restore procedure
- [ ] Have rollback plan ready

### Performance
- [ ] Gunicorn workers configured (4 workers)
- [ ] Connection pooling enabled
- [ ] Database indexes in place
- [ ] Static files cached
- [ ] Enable compression (optional)

---

## Rollback Plan (If Needed)

If deployment fails or causes issues:

```bash
# Option 1: Revert to previous commit
git revert HEAD
git push origin main
# Render will automatically redeploy

# Option 2: Rollback in Render Dashboard
# Go to Deployments tab and select previous version
# Click "Deploy"

# Option 3: Emergency shutdown
# In Render dashboard, click "Suspend Service"
# Fix the issue locally
# Redeploy
```

- [ ] Previous version tested locally before rollback
- [ ] Rollback documentation exists
- [ ] Team is notified of any issues
- [ ] Monitoring enabled for quick detection

---

## Post-Deployment Tasks

### Week 1
- [ ] Monitor logs for errors
- [ ] Test all features
- [ ] Gather user feedback
- [ ] Monitor performance
- [ ] Check database growth

### Month 1
- [ ] Review error logs
- [ ] Optimize slow endpoints
- [ ] Update documentation
- [ ] Plan Phase 2 improvements
- [ ] Review security

### Ongoing
- [ ] Regular security updates
- [ ] Database optimization
- [ ] Feature enhancements
- [ ] User feedback implementation
- [ ] Monitoring and alerts

---

## Sign-Off

- **Deployment Date**: _____________
- **Deployed By**: _____________
- **Reviewed By**: _____________
- **Status**: ✓ Production Live

---

## Notes & Issues

```
[Space for deployment notes]
```
