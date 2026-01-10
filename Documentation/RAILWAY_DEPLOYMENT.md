# VeinChain - Railway Deployment Guide

## Prerequisites
1. Railway.app account (free tier available)
2. GitHub account with repository pushed
3. PostgreSQL database (Railway provides)

## Deployment Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Fix critical issues and prepare for Railway deployment"
git push origin main
```

### Step 2: Create Railway Project
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Connect your GitHub account
5. Select your VeinChain repository

### Step 3: Configure Environment Variables
In Railway dashboard:
1. Go to your project
2. Click on the "Web" service
3. Go to "Variables" tab
4. Add the following:

```
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<generate-random-32-char-string>
JWT_SECRET_KEY=<generate-random-32-char-string>
SESSION_COOKIE_SECURE=True
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

To generate secure keys:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Add PostgreSQL Database
1. Click "New" in Railway
2. Select "PostgreSQL"
3. Railway will auto-set DATABASE_URL variable

### Step 5: Deploy
1. Railway automatically deploys when you push to GitHub
2. Watch the build logs in Railway dashboard
3. Once deployed, you'll get a URL like: `https://veinchain-prod.up.railway.app`

### Step 6: Verify Deployment
```bash
# Check health endpoint
curl https://yourrailway-url.app/health

# Response should be:
{"status":"ok"}
```

## Common Issues

### Issue: ImportError for models
**Fix**: Ensure all model files are in Backend/ directory and Procfile points to correct app

### Issue: Database not migrating
**Fix**: Railway runs migrations automatically. Check logs for errors.

### Issue: CORS errors in frontend
**Fix**: Update CORS_ORIGINS environment variable with your domain

### Issue: Static files not loading
**Fix**: Ensure Frontend directory structure is correct relative to Backend

## Production Checklist
- [ ] Change SECRET_KEY to random value
- [ ] Change JWT_SECRET_KEY to random value
- [ ] Set FLASK_ENV=production
- [ ] Set DEBUG=False
- [ ] Set SESSION_COOKIE_SECURE=True
- [ ] Update CORS_ORIGINS with your domain
- [ ] Setup email service (Gmail App Password or SendGrid)
- [ ] Test all API endpoints
- [ ] Monitor error logs
- [ ] Setup monitoring/alerts

## Rollback
If deployment fails:
1. Click "Build" in Railway
2. Select previous successful build
3. Click "Deploy" to rollback

## Support
For issues:
1. Check Railway logs: Click "Logs" in dashboard
2. Review error messages
3. Check GitHub Actions for deployment logs
4. Contact Railway support at railway.app
