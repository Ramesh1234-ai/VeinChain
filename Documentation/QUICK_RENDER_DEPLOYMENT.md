# VeinChain - Render Deployment Quick Reference

**TL;DR - Deploy in 5 minutes**

---

## Prerequisites

- [ ] GitHub account with VeinChain repository
- [ ] Render.com account (sign up with GitHub)
- [ ] Gmail account with 2FA enabled
- [ ] Generated SECRET_KEY and JWT_SECRET_KEY
- [ ] Gmail App Password (not regular password)

---

## Step 1: Generate Secret Keys

Run this in terminal:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
python -c "import secrets; print(secrets.token_hex(32))"
```

Save both outputs - you'll need them in Step 3.

---

## Step 2: Create Gmail App Password

1. Go to https://myaccount.google.com
2. Click "Security" (left sidebar)
3. Enable "2-Step Verification" if not done
4. Go back to Security
5. Scroll to "App Passwords"
6. Select "Mail" and your device
7. Copy the 16-character password

Save this - you'll need it in Step 3.

---

## Step 3: Push to GitHub

```bash
cd VeinChain

# Verify no credentials in code
git status

# Commit all changes
git add -A
git commit -m "Fix all code review issues - deploy to Render"
git push origin main

# Done! ✅
```

---

## Step 4: Deploy on Render

### Via Blueprint (Easiest - Recommended)

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Paste GitHub repo URL (or select from list)
4. Click "Connect"
5. Review `render.yaml` configuration
6. Click "Deploy Blueprint"
7. Wait ~3-5 minutes for build

### Via Web Service (Manual)

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Fill form:
   - **Name**: veinchain-backend
   - **Root Directory**: `Backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers 4 --worker-class sync --timeout 120 --bind 0.0.0.0:$PORT app:app`
   - **Runtime**: Python 3
   - **Plan**: Standard
5. Click "Create Web Service"
6. Follow Step 5 below to add environment variables

---

## Step 5: Configure Environment Variables

In Render Dashboard:

1. Go to your Web Service
2. Click "Environment" (left sidebar)
3. Add these variables:

```
FLASK_ENV = production
DEBUG = False
SECRET_KEY = (paste your generated key #1)
JWT_SECRET_KEY = (paste your generated key #2)
EMAIL_USER = your_gmail@gmail.com
EMAIL_PASS = (paste Gmail App Password)
CORS_ORIGINS = https://yourdomain.com
SESSION_COOKIE_SECURE = True
```

4. **For PostgreSQL** (recommended):
   - Click "Environment" again
   - Under "Data Services", click "Create PostgreSQL"
   - Copy "Internal Database URL"
   - Add to environment:
     ```
     DATABASE_URL = (paste Internal Database URL)
     ```

5. Click "Save"

---

## Step 6: Monitor Build

Watch the "Events" tab:

```
Status: Building
↓
Building image... (1-2 min)
↓
Deploying image... (1-2 min)
↓
Status: Live ✅
```

---

## Step 7: Test Your Deployment

```bash
# Get your URL from Render dashboard (e.g., veinchain-backend.onrender.com)

# Test home page
curl https://veinchain-backend.onrender.com/

# Test API
curl https://veinchain-backend.onrender.com/api/inventory

# Should see JSON response ✅
```

---

## Step 8: Custom Domain (Optional)

1. In Render, go to your Web Service
2. Click "Settings"
3. Scroll to "Custom Domains"
4. Add your domain
5. Note the CNAME record Render provides
6. Go to your domain provider (GoDaddy, Namecheap, etc.)
7. Add CNAME record pointing to Render
8. Wait 5-30 minutes for DNS to propagate
9. Your app is now at https://yourdomain.com

---

## Step 9: Update Frontend

Update your frontend to use production API:

### Option A: Environment Variable (Recommended)
```javascript
// In Frontend/static/js/config.js
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:5000'
  : '/api'  // Relative URL - auto-uses deployment domain
```

### Option B: Hard-coded URL (Not Recommended)
```javascript
const API_BASE_URL = 'https://veinchain-backend.onrender.com'
```

---

## Step 10: First Time Tests

### Test Registration
```bash
curl -X POST https://yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "name": "Test User",
    "role": "donor"
  }'

# Should return 201 with user data ✅
```

### Test Login
```bash
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Should return access_token ✅
```

### Test Protected Route
```bash
TOKEN="your_access_token_here"
curl https://yourdomain.com/api/notifications \
  -H "Authorization: Bearer $TOKEN"

# Should return notifications ✅
```

---

## Troubleshooting

### Build Failed
**Check Logs**:
1. In Render dashboard, click "Logs"
2. Look for error messages
3. Common fixes:
   - Missing environment variable → Add it
   - Import error → Check file names
   - Database error → Check DATABASE_URL format

### Application Won't Start
**Check**:
```
ERROR: No module named 'app'
→ Procfile is correct? (should be "app:app")

ERROR: No module named 'flask'
→ requirements.txt installed? (check build logs)

ERROR: Port already in use
→ Render handles port automatically (PORT env var)
```

### API Returning 404
**Check**:
- Is app running? (Status should be "Live")
- Is endpoint correct? (e.g., `/api/auth/login`)
- Are routes defined in app.py?

### CORS Errors in Frontend
**Fix**:
1. Add your frontend URL to CORS_ORIGINS:
   ```
   CORS_ORIGINS = https://yourdomain.com,https://www.yourdomain.com
   ```
2. Restart service (in Render dashboard, click "Restart")
3. Clear browser cache

### Email Not Sending
**Check**:
1. EMAIL_USER is correct Gmail
2. EMAIL_PASS is App Password (not regular password)
3. 2FA is enabled on Gmail account
4. No firewall blocking SMTP

**Test**:
```python
python -c "
import smtplib
smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
smtp.login('your_email@gmail.com', 'your_app_password')
print('✓ Email works!')
"
```

### Database Connection Failed
**Check**:
1. DATABASE_URL is set
2. Using **Internal** Database URL (not External)
3. Both web service and database in same region
4. Check Render PostgreSQL is running

---

## Monitoring

### Set Up Alerts

In Render Dashboard:

1. Go to your Web Service
2. Click "Alerts" (left sidebar)
3. Enable:
   - [ ] "Email on deploy failure"
   - [ ] "Email on service suspension"
   - [ ] "Email on critical alert"

### View Logs

In Render Dashboard:

1. Click "Logs" tab
2. Watch for:
   - Errors (red text)
   - Warnings (yellow text)
   - Info messages (gray text)

### Monitor Performance

In Render Dashboard:

1. Click "Metrics" tab
2. Watch:
   - CPU usage
   - Memory usage
   - Response time
   - Error rate

---

## Auto-Deploy from GitHub

Automatic redeployment on every push to `main`:

1. In Render dashboard, go to Web Service
2. Click "Settings"
3. Scroll to "Auto-Deploy"
4. Select "Yes" for main branch
5. Every `git push origin main` will auto-deploy

---

## Restart Service

If you need to restart (after changing env vars):

1. In Render dashboard, go to Web Service
2. Click "Restart" button
3. Service restarts in ~30 seconds
4. No downtime

---

## Suspend/Resume Service

To pause service (save $$):

1. Click "Suspend" in Render dashboard
2. Service stops, no more charges
3. Click "Resume" to restart

---

## Delete Service

To remove service:

1. In Render dashboard, go to Web Service
2. Click "Settings"
3. Scroll to "Danger Zone"
4. Click "Delete Web Service"
5. Confirm deletion

---

## Success Checklist

- [ ] Environment variables set
- [ ] Build status is "Live"
- [ ] Home page loads (/)
- [ ] API responds (/api/inventory)
- [ ] Auth works (registration/login)
- [ ] Protected routes work
- [ ] Email sends (if configured)
- [ ] Database persists data
- [ ] No errors in logs
- [ ] Frontend connects to backend

---

## Final Notes

- **Build time**: 3-5 minutes
- **Deploy time**: 30 minutes total (including setup)
- **Cost**: Starting at $7/month
- **Downtime**: Zero (Render handles)
- **SSL/HTTPS**: Automatic (free)
- **Backups**: Automatic (PostgreSQL)

---

## That's It! 🎉

Your VeinChain application is now live in production on Render!

### Next: Tell Us About It
- Update your website
- Notify stakeholders
- Monitor for issues
- Plan Phase 2 improvements

---

## Emergency Contacts

- **Render Support**: https://render.com/support
- **Flask Docs**: https://flask.palletsprojects.com/
- **GitHub Issues**: Create issue on your repo

---

**Deployment Date**: January 10, 2026  
**Status**: ✅ Production Live

🚀 **Congratulations!**
