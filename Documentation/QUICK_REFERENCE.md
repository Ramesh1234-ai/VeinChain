# VeinChain - Quick Reference Guide

## 📋 Frontend Forms to Backend Connection Status

### ✅ All Forms Connected & Working

| Form | Endpoint | Database | Email | Status |
|------|----------|----------|-------|--------|
| **Login** | POST /api/auth/login | User ✓ | N/A | ✅ Working |
| **Register** | POST /api/auth/register | User, Donor, Notification ✓ | Welcome ✓ | ✅ Working |
| **Blood Request** | POST /api/blood-requests | BloodRequest, Notification ✓ | Confirmation ✓ | ✅ Working |
| **Donation** | POST /api/donations | Donation, Donor, Notification ✓ | Thank You ✓ | ✅ Working |
| **Contact Us** | POST /api/contact | ContactMessage ✓ | N/A | ✅ Working |
| **Admin Panel** | Multiple /admin/* | Donor, BloodRequest, Notification ✓ | Approval ✓ | ✅ Working |

---

## 🔗 Data Flow Architecture

```
User Interface (Frontend HTML Forms)
        ↓
   Fetch API (JSON)
        ↓
Backend Endpoints (/api/*)
        ↓
SQLAlchemy ORM
        ↓
SQLite Database (blood_donation.db)
        ↓
Email Service (Gmail SMTP)
        ↓
User Email Inbox
```

---

## 📡 API Endpoints by Category

### **Auth Endpoints** (No Auth Required)
```
POST   /api/auth/register       → Creates User + Donor records
POST   /api/auth/login          → Authenticates user, returns JWT
POST   /api/auth/firebase-login → Firebase Google Sign-in
POST   /verify_token            → Verifies Firebase token
```

### **Protected Endpoints** (JWT Required)
```
GET    /api/auth/status         → Check if logged in
POST   /api/auth/logout         → Logout user
GET    /api/notifications       → Get user notifications
POST   /api/donations           → Record blood donation (Donor only)
POST   /api/blood-requests      → Submit blood request
```

### **Admin Endpoints** (JWT + Admin Role Required)
```
GET    /admin/pending-donors            → List pending donors
PUT    /admin/approve-donor/<id>        → Approve donor
DELETE /admin/reject-donor/<id>         → Reject donor
GET    /admin/pending-requests          → List pending requests
PUT    /admin/approve-request/<id>      → Approve request
DELETE /admin/reject-request/<id>       → Reject request
```

### **Public Endpoints** (No Auth Required)
```
POST   /api/contact              → Submit contact message
GET    /api/inventory            → Get blood inventory
```

---

## 🗄️ Database Tables & Connections

### User Table
- Stores login credentials
- Stores user role (admin, donor, recipient)
- **Connected Forms**: Login, Register

### Donor Table
- Stores donor-specific info (blood type, status)
- Status: pending → approved → active
- **Connected Forms**: Register (auto-created), Admin Panel (approval)

### BloodRequest Table
- Stores blood requests from recipients
- Status tracking: pending → approved
- **Connected Forms**: Blood Request form, Admin Panel

### Donation Table
- Records actual blood donations
- Updates Donor's last_donation_date
- **Connected Forms**: Donation form

### ContactMessage Table
- Stores contact form submissions
- **Connected Forms**: Contact Us form

### Notification Table
- Stores all system notifications
- Retrieved via /api/notifications endpoint
- **Connected Forms**: All forms (auto-created)

---

## 🔐 Authentication & Authorization

### Login Flow
1. User enters email/password in login form
2. Frontend sends POST /api/auth/login
3. Backend validates against User table
4. If valid → Returns JWT token + user data
5. Frontend stores token in localStorage
6. Token sent with all protected requests

### Protected Routes
- Require `Authorization: Bearer <token>` header
- Token decoded and validated server-side
- User info extracted from token
- Request processed or denied based on role

### Roles
- **Admin**: Can approve/reject donors and blood requests
- **Donor**: Can submit blood donations
- **Recipient**: Can request blood
- **User**: Basic user (default)

---

## 📧 Email Notifications

### Automatic Emails Sent For:
1. **Registration** → Welcome email to new user
2. **Donation** → Thank you email to donor
3. **Blood Request** → Confirmation email to recipient
4. **Admin Approval** → Approval notification email
5. **Admin Rejection** → Rejection notification email

### Configuration
- Service: Gmail SMTP
- Port: 465 (SSL)
- Credentials: EMAIL_USER, EMAIL_PASS (environment variables)

---

## 🚀 Running the Application

### Backend
```bash
cd Backend
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000
```

### Database
- Auto-created on first run
- Location: Backend/instance/blood_donation.db
- Tables auto-created via SQLAlchemy

### Frontend
- Served from: http://localhost:5000/
- Templates: Frontend/templates/*.html
- Static: Frontend/static/

---

## 📊 Form Submission Flow Example: Register

```
1. User fills registration form
   ↓
2. Frontend validates input
   ↓
3. Frontend sends POST /api/auth/register
   {name, email, password, role, blood_type}
   ↓
4. Backend receives request
   ↓
5. Backend validates (check email unique, required fields)
   ↓
6. Backend hashes password with werkzeug
   ↓
7. Backend creates User record in SQLite
   ↓
8. If role='donor', creates Donor record with status='pending'
   ↓
9. Backend creates Notification record
   ↓
10. Backend sends welcome email via Gmail SMTP
    ↓
11. Frontend receives success response
    ↓
12. Frontend redirects user to login page
    ↓
13. Email arrives in user's inbox
```

---

## 🔍 Testing Each Form

| Form | Test Steps |
|------|-----------|
| **Register** | 1. Go to /register.html<br/>2. Fill all fields<br/>3. Submit<br/>4. Check email for welcome message |
| **Login** | 1. Go to /login.html<br/>2. Enter registered email/password<br/>3. Should redirect to dashboard |
| **Blood Request** | 1. Login as recipient<br/>2. Go to /Recipent.html<br/>3. Fill blood request form<br/>4. Check notifications |
| **Donation** | 1. Login as donor<br/>2. Go to /dashboard.html<br/>3. Fill donation form<br/>4. Check notifications |
| **Contact** | 1. Go to /Contact Us.html<br/>2. Fill contact form<br/>3. Submit<br/>4. Message saved in database |
| **Admin** | 1. Login as admin<br/>2. Go to /adminPanel.html<br/>3. View pending items<br/>4. Approve/reject<br/>5. Check notifications sent |

---

## ✅ Verification Checklist

- [x] All frontend forms have corresponding backend endpoints
- [x] All endpoints connected to appropriate database tables
- [x] Authentication implemented with JWT tokens
- [x] Role-based access control working
- [x] Email notifications operational
- [x] Database auto-created on startup
- [x] Session management functional
- [x] CORS configured for frontend origin
- [x] Admin approval workflow operational
- [x] Error handling in place

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Token missing" error | Check Authorization header in fetch requests |
| "Email already registered" | Use unique email in registration form |
| Emails not sending | Check EMAIL_USER and EMAIL_PASS environment variables |
| 403 Forbidden on admin routes | Ensure logged-in user has 'admin' role |
| 401 Unauthorized | Re-login to get fresh JWT token |
| Database not created | Run app.py, it auto-creates on first run |

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| Backend/app.py | All backend routes and logic |
| Backend/database.py | Database models definition |
| Backend/config.py | Configuration settings |
| Frontend/templates/login.html | Login form |
| Frontend/templates/register.html | Registration form |
| Frontend/templates/Recipent.html | Blood request form |
| Frontend/templates/dashboard.html | Donation form & inventory |
| Frontend/templates/Contact Us.html | Contact form |
| Frontend/templates/adminPanel.html | Admin approval panel |

---

## 🎯 Connection Summary

### Frontend → Backend: ✅ 100% Connected
All HTML forms have matching backend endpoints

### Backend → Database: ✅ 100% Connected
All endpoints interact with database tables

### Notifications: ✅ 100% Operational
- Database notifications in Notification table
- Email notifications via Gmail SMTP
- Frontend retrieval via /api/notifications

### Authentication: ✅ 100% Secured
- JWT tokens with expiration
- Password hashing
- Role-based access control

---

## 📞 Support

For detailed information, see:
- [README.md](README.md) - Full project documentation
- [ENDPOINTS_ANALYSIS.md](ENDPOINTS_ANALYSIS.md) - Detailed endpoint analysis
- Backend/app.py - Source code with inline comments

---

**Status**: ✅ ALL SYSTEMS OPERATIONAL
**Last Updated**: January 9, 2026
**VeinChain Blood Donation Management System**
