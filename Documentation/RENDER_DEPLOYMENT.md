# VeinChain - Render Deployment Guide

## Pre-Deployment Checklist

- [ ] All credentials removed from code (Firebase keys, Gmail password)
- [ ] Environment variables configured
- [ ] Database migrations tested locally
- [ ] All endpoints tested locally
- [ ] Frontend CORS origins updated

---

## Step 1: Prepare Your Repository

### Remove Credentials from Git History

```bash
# If you have exposed credentials in git history, remove them:
git filter-branch --tree-filter 'rm -f Backend/.env Backend/firebase_config.json' HEAD

# Or use BFG (faster for large repos)
bfg --delete-files .env --delete-files firebase_config.json
```

### Verify .gitignore

Ensure these entries exist in `.gitignore`:
```
.env
.env.local
.env.*.local
Backend/firebase_config.json
instance/
__pycache__/
*.pyc
.DS_Store
.venv/
venv/
*.db
flask_session/
```

---

## Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your GitHub repository

---

## Step 3: Generate Secure Keys

Generate new secret keys for production:

```bash
# Option 1: Using Python
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"

# Option 2: Using OpenSSL
openssl rand -hex 32
openssl rand -hex 32
```

Save these keys somewhere safe - you'll need them for Render dashboard.

---

## Step 4: Deploy on Render

### Option A: Using render.yaml (Recommended)

1. The `render.yaml` file is already in the repo root
2. Push to GitHub
3. Go to [Render Dashboard](https://dashboard.render.com)
4. Click "New +" > "Blueprint"
5. Select your GitHub repository
6. Review the configuration
7. Click "Deploy"

### Option B: Manual Deployment

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" > "Web Service"
3. Connect GitHub repository
4. Fill in the form:
   - **Name**: veinchain-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r Backend/requirements.txt`
   - **Start Command**: `cd Backend && gunicorn --workers 4 --worker-class sync --timeout 120 --bind 0.0.0.0:$PORT app:app`
   - **Region**: Choose closest to your users (e.g., Oregon)
   - **Plan**: Standard ($7/month)

### Step 5: Configure Environment Variables

In Render Dashboard, go to your Web Service > Environment:

Add these environment variables:

```
FLASK_ENV = production
DEBUG = False
SECRET_KEY = (paste generated key)
JWT_SECRET_KEY = (paste generated key)
EMAIL_USER = your_gmail@gmail.com
EMAIL_PASS = your_app_password_here
CORS_ORIGINS = https://yourdomain.com,https://www.yourdomain.com
SESSION_COOKIE_SECURE = True
DATABASE_URL = (auto-provided if using Render PostgreSQL)
```

### Step 6: Add PostgreSQL Database (Recommended)

For production, use PostgreSQL instead of SQLite:

1. In Render Dashboard, click "New +" > "PostgreSQL"
2. Fill in the form:
   - **Name**: veinchain-db
   - **Database**: veinchain
   - **User**: veinchain_user
   - **Region**: Same as web service
   - **Plan**: Standard ($15/month)

3. Once created, copy the `Internal Database URL`
4. In Web Service Environment, set:
   ```
   DATABASE_URL = (paste the internal URL)
   ```

### Step 7: Update Database on Deployment

The `render.yaml` includes a build command that will initialize the database:

```bash
pip install -r Backend/requirements.txt
python Backend/app.py  # This runs db.create_all()
```

To run migrations after first deployment:

1. Connect to your instance via SSH (Render provides this in dashboard)
2. Run:
   ```bash
   flask db upgrade
   ```

---

## Step 8: Update Frontend CORS

In `render.yaml`, update CORS_ORIGINS to your domain:

```yaml
CORS_ORIGINS: https://yourdomain.com,https://www.yourdomain.com
```

Or set it in the Render dashboard.

---

## Step 9: Gmail App Password

For email notifications to work:

1. Go to [Google Account](https://myaccount.google.com)
2. Click "Security" in left menu
3. Enable "2-Step Verification" if not already done
4. Go back to Security, scroll down to "App Passwords"
5. Select "Mail" and "Windows (or your device)"
6. Google generates a 16-character password
7. Copy and paste as `EMAIL_PASS` in Render dashboard

**IMPORTANT**: Don't use your regular Google password!

---

## Step 10: Configure Firebase (Optional)

If using Firebase authentication:

1. Download your Firebase service account JSON from Google Cloud Console
2. In Render dashboard, you can't directly upload files
3. Instead, create a secret file or configure via environment variable:

```python
# In app.py, load from environment variable
firebase_config_json = os.getenv('FIREBASE_CONFIG_JSON')
if firebase_config_json:
    cred = credentials.Certificate(json.loads(firebase_config_json))
```

Or better: Use Firebase REST API instead of Admin SDK.

---

## Step 11: Monitor Deployment

### Check Build Logs

1. Go to your service in Render Dashboard
2. Click "Logs" tab
3. You should see:
   ```
   ✓ Build succeeded
   ✓ Deployment in progress
   ```

### Test Your API

Once deployed, you'll get a URL like: `https://veinchain-backend.onrender.com`

Test the health endpoint:

```bash
curl https://veinchain-backend.onrender.com/
# Should return HTML of home page
```

Test an API endpoint:

```bash
curl https://veinchain-backend.onrender.com/api/inventory
# Should return JSON with blood inventory
```

---

## Step 12: Set Up Custom Domain (Optional)

1. In Render Dashboard, go to your Web Service
2. Click "Settings" tab
3. Scroll to "Custom Domains"
4. Add your domain
5. Update your domain's DNS records (Render provides instructions)

---

## Troubleshooting

### "Application failed to start"

Check logs for errors:
```
ERROR: No module named 'database'
```

**Solution**: Make sure imports in app.py use relative paths:
```python
from database import db, User, Donor, ...  # ✓ Correct
from Backend.database import db  # ✗ Wrong
```

### "ModuleNotFoundError: No module named 'firebase_admin'"

**Solution**: Ensure `firebase-admin` is in requirements.txt or it's marked optional:
```python
try:
    from firebase_admin import auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
```

### "Database connection refused"

**Solution**: 
1. Check `DATABASE_URL` is set correctly
2. Make sure it uses the **Internal Database URL** (not External)
3. Ensure web service and database are in same region

### CORS errors in frontend

**Solution**: Update `CORS_ORIGINS` in Render dashboard:
```
https://yourdomain.com,https://www.yourdomain.com,http://localhost:5500
```

### Email not sending

**Solution**:
1. Verify `EMAIL_USER` and `EMAIL_PASS` are correct
2. Check 2FA is enabled on Gmail
3. Use App Password (not regular password)
4. Test with:
   ```bash
   python -c "
   import smtplib
   smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
   smtp.login('your_email@gmail.com', 'your_app_password')
   print('✓ Gmail works!')
   "
   ```

---

## Post-Deployment Steps

### 1. Test All Features

```bash
# Test registration
curl -X POST https://yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'

# Test login
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Test protected route
curl https://yourdomain.com/api/inventory
```

### 2. Set Up Monitoring

In Render Dashboard > Alerts:
- Enable email alerts for deployment failures
- Set up uptime monitoring
- Configure error notifications

### 3. Enable Auto-Deploys

In Render Dashboard > Settings:
- Enable "Auto-Deploy" for `main` branch
- Any push to main will automatically redeploy

### 4. Update Frontend API URLs

Update your frontend environment to use the production API:

In `Frontend/static/js/config.js`:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:5000'
  : 'https://yourdomain.com'
```

---

## Security Checklist - Before Going Live

- [ ] All credentials in `.env`, NOT in code
- [ ] `.gitignore` includes `.env` and `firebase_config.json`
- [ ] `SESSION_COOKIE_SECURE = True` in production
- [ ] `FLASK_ENV = production`
- [ ] `DEBUG = False`
- [ ] SECRET_KEY and JWT_SECRET_KEY are strong random strings
- [ ] Email password is an App Password, not Gmail password
- [ ] CORS origins are restricted to your domain(s)
- [ ] Rate limiting is enabled on auth endpoints
- [ ] Input validation on all endpoints
- [ ] HTTPS enforced (Render does this automatically)
- [ ] Database backups configured (if using Render PostgreSQL)

---

## Useful Render Commands

### View Logs
```bash
# In Render dashboard, click "Logs" tab
```

### Restart Service
```bash
# In Render dashboard, click "Restart"
```

### Scale Up/Down
```bash
# In Render dashboard > Settings > Plan
```

### Database Connection
```bash
# Get connection string from Render PostgreSQL dashboard
# Use with pgAdmin or any PostgreSQL client
```

---

## Additional Resources

- [Render Docs](https://render.com/docs)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
- [PostgreSQL Best Practices](https://www.postgresql.org/docs/current/sql-syntax.html)

---

**Congratulations!** Your VeinChain application is now live on Render! 🚀
