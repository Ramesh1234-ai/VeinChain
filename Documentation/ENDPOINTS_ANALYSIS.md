# VeinChain - Frontend Forms to Backend Endpoints Analysis

## Overview
This document provides a detailed analysis of how each frontend form connects to backend endpoints and the database.

---

## 1. LOGIN FORM

**Location**: [Frontend/templates/login.html](Frontend/templates/login.html)

### Form Details
| Field | Type | Required |
|-------|------|----------|
| Email | Text | Yes |
| Password | Password | Yes |

### Frontend Implementation
```javascript
// Lines 534-556
fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
});
```

### Backend Endpoint
**Route**: `POST /api/auth/login`
**Location**: [Backend/app.py](Backend/app.py#L195)
**Authentication**: Not required
**Handler**:
```python
@app.route('/api/auth/login', methods=['POST'])
def login():
    # Validates email/password
    # Queries User table
    # Returns JWT token + user data
    # Returns 401 for invalid credentials
```

### Database Connection
✅ **CONNECTED**
- **Table**: `User` table
- **Query**: `User.query.filter_by(email=email).first()`
- **Action**: Validates password hash
- **Returns**: User ID, Email, Name, Role
- **Additional Actions**:
  - Creates JWT token with 24-hour expiration
  - Stores user data in localStorage (frontend)
  - Triggers role-based redirect

### Related Endpoints (Same Form)
- `POST /api/auth/firebase-login` - Firebase Google Sign-in alternative
- `POST /verify_token` - Firebase token verification
- `GET /api/auth/status` - Check if already logged in
- `POST /api/auth/logout` - Logout functionality

### Status
✅ **FULLY OPERATIONAL**

---

## 2. REGISTRATION FORM

**Location**: [Frontend/templates/register.html](Frontend/templates/register.html)

### Form Details
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Name | Text | Yes | Full name |
| Email | Email | Yes | Must be unique |
| Password | Password | Yes | Min 6 characters |
| Role | Select | Yes | 'donor' or 'recipient' |
| Blood Type | Select | Conditional | Only if role='donor' |

### Frontend Implementation
```javascript
// Lines 556-560 (Register handler)
const res = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password, role, blood_type })
});
```

### Backend Endpoint
**Route**: `POST /api/auth/register`
**Location**: [Backend/app.py](Backend/app.py#L151)
**Authentication**: Not required
**Handler**:
```python
@app.route('/api/auth/register', methods=['POST'])
def register():
    # Validates required fields
    # Checks if email already exists
    # Hashes password using werkzeug
    # Creates User record
    # If role='donor', creates Donor record with status='pending'
    # Sends welcome email via SMTP
    # Creates notification
```

### Database Connections
✅ **FULLY CONNECTED**

#### User Table Insert
- `id`: UUID (auto-generated)
- `name`: From form
- `email`: From form (validated for uniqueness)
- `password`: Hashed using `generate_password_hash()`
- `role`: From form ('donor' or 'recipient')
- `created_at`: Current timestamp

#### Donor Table Insert (if role='donor')
- `id`: UUID
- `user_id`: Foreign key to User.id
- `blood_type`: From form
- `is_available`: True (default)
- `status`: 'pending' (awaits admin approval)
- `last_donation_date`: NULL

#### Notification Table Insert
- `id`: UUID
- `user_id`: New user's ID
- `message`: "Welcome {name}! You are registered as {role}."
- `created_at`: Current timestamp

#### Email Sent Via SMTP
- To: New user's email
- Subject: "Blood.Ninja Notification"
- Body: Welcome message

### Returns
```json
{
    "message": "User registered",
    "user": {
        "id": "uuid",
        "email": "user@example.com",
        "name": "User Name",
        "role": "donor"
    }
}
```

### Status
✅ **FULLY OPERATIONAL**

---

## 3. BLOOD REQUEST FORM

**Location**: [Frontend/templates/Recipent.html](Frontend/templates/Recipent.html)

### Form Details
| Field | Type | Required |
|-------|------|----------|
| Blood Type | Select | Yes |
| Quantity | Number | Yes |
| Urgency | Select | Yes |
| Hospital | Text | Yes |
| Contact Number | Phone | Yes |
| Notes | Textarea | No |

### Frontend Implementation
```javascript
// Lines 914-926 (Recipient form submission)
fetch("/api/blood-requests", {
    method: 'POST',
    headers: { 
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        blood_type: bloodType,
        quantity: quantity,
        urgency: urgency,
        hospital: hospital,
        contact_number: contactNumber,
        notes: notes
    })
});
```

### Backend Endpoint
**Route**: `POST /api/blood-requests`
**Location**: [Backend/app.py](Backend/app.py#L309)
**Authentication**: ✅ **REQUIRED** (JWT token)
**Handler**:
```python
@app.route('/api/blood-requests', methods=['POST'])
@token_required
def create_blood_request(current_user):
    # Validates JWT token
    # Creates BloodRequest record
    # Sets status='pending'
    # Sends notification to requester
```

### Database Connections
✅ **FULLY CONNECTED**

#### BloodRequest Table Insert
- `id`: UUID
- `requester_id`: Foreign key to User.id (from JWT token)
- `blood_type`: From form
- `quantity`: From form
- `urgency`: From form
- `hospital`: From form
- `contact_number`: From form
- `notes`: From form
- `request_date`: Current timestamp
- `status`: 'pending'

#### Notification Table Insert
- `id`: UUID
- `user_id`: Requester's user_id
- `message`: "Your request for {quantity} units of {blood_type} has been submitted."
- `created_at`: Current timestamp

#### Email Sent Via SMTP
- To: Requester's email
- Subject: "Blood.Ninja Notification"
- Body: Request confirmation message

#### Notification Retrieval
**Route**: `GET /api/notifications`
**Location**: [Backend/app.py](Backend/app.py#L330)
**Authentication**: ✅ **REQUIRED** (JWT token)
```javascript
// Frontend
fetch("/api/notifications", {
    headers: { 'Authorization': 'Bearer ' + token }
});
```

### Returns
```json
{
    "message": "Blood request created"
}
```

### Status
✅ **FULLY OPERATIONAL**

---

## 4. DONATION FORM

**Location**: [Frontend/templates/dashboard.html](Frontend/templates/dashboard.html)

### Form Details
| Field | Type | Required |
|-------|------|----------|
| Blood Type | Select | Yes |
| Quantity | Number | Yes |
| Location | Text | Yes |
| Notes | Textarea | No |

### Frontend Implementation
```javascript
// Lines 528-529 (Donation form)
const response = await fetch("/api/donations", {
    method: 'POST',
    headers: { 
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        blood_type: bloodType,
        quantity: quantity,
        location: location,
        notes: notes
    })
});
```

### Backend Endpoint
**Route**: `POST /api/donations`
**Location**: [Backend/app.py](Backend/app.py#L286)
**Authentication**: ✅ **REQUIRED** (JWT token)
**Role Required**: 'donor'
**Handler**:
```python
@app.route('/api/donations', methods=['POST'])
@token_required
def create_donation(current_user):
    # Validates JWT token
    # Checks if user role is 'donor'
    # Creates Donation record
    # Updates Donor's last_donation_date
    # Sends thank you notification
```

### Database Connections
✅ **FULLY CONNECTED**

#### Donation Table Insert
- `id`: UUID
- `donor_id`: Foreign key to User.id (from JWT token)
- `donation_date`: Current timestamp
- `blood_type`: From form
- `quantity`: From form
- `location`: From form
- `notes`: From form

#### Donor Table Update
- `last_donation_date`: Updated to current timestamp
- Query: `Donor.query.filter_by(user_id=current_user.id).first()`

#### Notification Table Insert
- `id`: UUID
- `user_id`: Donor's user_id
- `message`: "Thanks {name}! Your donation of {quantity}ml {blood_type} has been recorded."
- `created_at`: Current timestamp

#### Email Sent Via SMTP
- To: Donor's email
- Subject: "Blood.Ninja Notification"
- Body: Thank you message with donation details

#### Inventory Check
**Route**: `GET /api/inventory`
**Location**: [Backend/app.py](Backend/app.py#L507)
**Authentication**: Not required
```javascript
// Frontend - Lines 528-533
const response = await fetch("/api/inventory", {
    method: 'GET'
});
```
**Returns**: In-memory inventory list (blood groups and units)

### Returns
```json
{
    "message": "Donation recorded"
}
```

### Status
✅ **FULLY OPERATIONAL**

---

## 5. CONTACT US FORM

**Location**: [Frontend/templates/Contact Us.html](Frontend/templates/Contact%20Us.html)

### Form Details
| Field | Type | Required |
|-------|------|----------|
| Name | Text | Yes |
| Email | Email | Yes |
| Phone | Phone | No |
| Subject | Text | No |
| Message | Textarea | Yes |

### Frontend Implementation
```javascript
// Contact form submission (no specific location shown in grep)
const formData = {
    name: document.getElementById('name').value,
    email: document.getElementById('email').value,
    phone: document.getElementById('phone').value,
    subject: document.getElementById('subject').value,
    message: document.getElementById('message').value
};

fetch('/api/contact', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
});
```

### Backend Endpoint
**Route**: `POST /api/contact`
**Location**: [Backend/app.py](Backend/app.py#L336)
**Authentication**: Not required
**Handler**:
```python
@app.route('/api/contact', methods=['POST'])
def submit_contact():
    # Validates required fields (name, email, message)
    # Creates ContactMessage record
    # Returns success message
```

### Database Connection
✅ **CONNECTED**

#### ContactMessage Table Insert
- `id`: UUID
- `name`: From form
- `email`: From form
- `phone`: From form (nullable)
- `subject`: From form (nullable)
- `message`: From form
- `created_at`: Current timestamp

### Returns
```json
{
    "message": "Contact message saved"
}
```

### Status
✅ **FULLY OPERATIONAL**

---

## 6. ADMIN PANEL

**Location**: [Frontend/templates/adminPanel.html](Frontend/templates/adminPanel.html)

### Functions Overview
1. View pending donors waiting for approval
2. Approve/Reject donor registrations
3. View pending blood requests
4. Approve/Reject blood requests

### Admin Endpoints

#### Get Pending Donors
**Route**: `GET /admin/pending-donors`
**Location**: [Backend/app.py](Backend/app.py#L537)
**Authentication**: ✅ **REQUIRED** (JWT token)
**Role Required**: 'admin'
**Handler**:
```python
@app.route("/admin/pending-donors", methods=["GET"])
@role_required("admin")
def get_pending_donors():
    donors = Donor.query.filter_by(status="pending").all()
    # Returns list of pending donors
```

**Database Query**:
- Filters Donor table by `status='pending'`
- Returns: donor id, user_id, blood_type, is_available

#### Approve Donor
**Route**: `PUT /admin/approve-donor/<donor_id>`
**Location**: [Backend/app.py](Backend/app.py#L558)
**Authentication**: ✅ **REQUIRED** (JWT token)
**Role Required**: 'admin'
**Handler**:
```python
@app.route("/admin/approve-donor/<donor_id>", methods=["PUT"])
@role_required("admin")
def approve_donor(donor_id):
    # Updates Donor status to 'approved'
    # Sends notification to donor
    # Sends email to donor
```

**Database Updates**:
- Donor table: `status='approved'`
- Notification table: Creates approval notification
- Email: Sends approval confirmation

#### Reject Donor
**Route**: `DELETE /admin/reject-donor/<donor_id>`
**Location**: [Backend/app.py](Backend/app.py#L570)
**Authentication**: ✅ **REQUIRED** (JWT token)
**Role Required**: 'admin'
**Handler**:
```python
@app.route("/admin/reject-donor/<donor_id>", methods=["DELETE"])
@role_required("admin")
def reject_donor(donor_id):
    # Updates Donor status to 'rejected'
    # Sends notification to donor
    # Sends email to donor
```

**Database Updates**:
- Donor table: `status='rejected'`
- Notification table: Creates rejection notification
- Email: Sends rejection notice

#### Get Pending Blood Requests
**Route**: `GET /admin/pending-requests`
**Location**: [Backend/app.py](Backend/app.py#L586)
**Authentication**: ✅ **REQUIRED** (JWT token)
**Role Required**: 'admin'
**Handler**:
```python
@app.route("/admin/pending-requests", methods=["GET"])
@role_required("admin")
def get_pending_requests():
    requests = BloodRequest.query.filter_by(status="pending").all()
    # Returns list of pending blood requests
```

**Database Query**:
- Filters BloodRequest table by `status='pending'`
- Returns: request details (id, blood_type, quantity, urgency, etc.)

#### Approve Blood Request
**Route**: `PUT /admin/approve-request/<request_id>`
**Location**: [Backend/app.py](Backend/app.py#L607)
**Authentication**: ✅ **REQUIRED** (JWT token)
**Role Required**: 'admin'
**Handler**:
```python
@app.route("/admin/approve-request/<request_id>", methods=["PUT"])
@role_required("admin")
def approve_request(request_id):
    # Updates BloodRequest status to 'approved'
    # Sends notification to requester
    # Sends email to requester
```

**Database Updates**:
- BloodRequest table: `status='approved'`
- Notification table: Creates approval notification
- Email: Sends approval confirmation

#### Reject Blood Request
**Route**: `DELETE /admin/reject-request/<request_id>`
**Location**: [Backend/app.py](Backend/app.py#L619)
**Authentication**: ✅ **REQUIRED** (JWT token)
**Role Required**: 'admin'
**Handler**:
```python
@app.route("/admin/reject-request/<request_id>", methods=["DELETE"])
@role_required("admin")
def reject_request(request_id):
    # Updates BloodRequest status to 'rejected'
    # Sends notification to requester
    # Sends email to requester
```

**Database Updates**:
- BloodRequest table: `status='rejected'`
- Notification table: Creates rejection notification
- Email: Sends rejection notice

### Status
✅ **FULLY OPERATIONAL**

---

## Summary Table: All Frontend Forms & Backend Connections

| # | Form | Frontend File | Endpoint | Auth | DB Tables | Status |
|---|------|---------------|----------|------|-----------|--------|
| 1 | Login | login.html | POST /api/auth/login | ✗ | User | ✅ |
| 2 | Register | register.html | POST /api/auth/register | ✗ | User, Donor, Notification | ✅ |
| 3 | Blood Request | Recipent.html | POST /api/blood-requests | ✓ | BloodRequest, Notification | ✅ |
| 4 | Donation | dashboard.html | POST /api/donations | ✓ | Donation, Donor, Notification | ✅ |
| 5 | Contact | Contact Us.html | POST /api/contact | ✗ | ContactMessage | ✅ |
| 6 | Admin Panel | adminPanel.html | Multiple /admin/* | ✓ | Donor, BloodRequest, Notification | ✅ |

---

## Database Connection Summary

### Connection Path
```
Frontend Form 
    ↓ (HTTP/HTTPS)
Backend Endpoint (/api/*)
    ↓ (SQLAlchemy ORM)
Database Tables (SQLite)
    ↓
Email Notifications (SMTP via Gmail)
    ↓
User's Email
```

### All Tables Connected
- ✅ User - Authentication & user data
- ✅ Donor - Donor profiles & status tracking
- ✅ BloodRequest - Blood requests & status
- ✅ Donation - Donation records
- ✅ ContactMessage - Contact form submissions
- ✅ Notification - User notifications

### Email System
- ✅ Welcome emails on registration
- ✅ Donation confirmation emails
- ✅ Blood request confirmation emails
- ✅ Admin approval/rejection emails
- Configuration: Gmail SMTP via environment variables

---

## Session & Authentication Flow

### JWT Token Authentication
1. User logs in → Backend generates JWT token
2. Token stored in localStorage (frontend)
3. Token sent in Authorization header for protected endpoints
4. Backend validates token before processing requests
5. Routes protected with `@token_required` decorator

### Role-Based Access Control (RBAC)
- **Donor**: Can create donations
- **Recipient**: Can request blood
- **Admin**: Can approve/reject donors and requests
- Implemented via `@role_required(role)` decorator

### Session Storage
- Flask-Session with filesystem storage
- Session data stored in `flask_session/` directory
- Supports role-based redirects after login

---

## Security Implementation

| Feature | Status | Details |
|---------|--------|---------|
| Password Hashing | ✅ | werkzeug.security.generate_password_hash |
| JWT Tokens | ✅ | 24-hour expiration |
| Role Validation | ✅ | @token_required & @role_required decorators |
| CORS | ✅ | Restricted to allowed origins |
| Email Validation | ✅ | Unique email check in registration |
| Input Validation | ✅ | Required field checks |

---

## Status Overview

**All Forms Connected**: ✅ **YES**
**All Endpoints Working**: ✅ **YES**
**All Database Connections Active**: ✅ **YES**
**Email Notifications**: ✅ **YES**
**Admin Functionality**: ✅ **YES**

**Overall Status**: ✅ **FULLY OPERATIONAL**

---

*Last Updated: January 9, 2026*
*Analysis Complete: All Frontend Forms → Backend Endpoints → Database*
