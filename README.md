# VeinChain - Blood Donation Management System

A comprehensive blood donation management platform built with Flask backend and modern HTML/CSS/JavaScript frontend. The system connects donors and recipients, manages blood requests and donations, and provides an admin panel for approval workflows.

## Project Overview

VeinChain is a web application designed to streamline blood donation processes by:
- Managing user registration (Donors, Recipients, Admins)
- Facilitating blood donation tracking
- Processing blood requests
- Handling donor/recipient matching
- Providing notifications and contact management
- Admin dashboard for approval workflows

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite (`blood_donation.db`)
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens, Firebase Admin SDK
- **Email**: SMTP Gmail integration
- **Session Management**: Flask-Session (filesystem storage)

### Frontend
- **HTML5** with responsive design
- **CSS3** with animations and gradients
- **JavaScript** (ES6+) with Fetch API
- **Firebase Authentication** (Google Sign-in)
- **Icons**: Font Awesome 6.4.0

## Database Models

The application uses the following database models:

### User Model
```python
- id (String, Primary Key)
- name (String, 100 chars)
- email (String, unique)
- password (String, hashed)
- role (String: 'user', 'donor', 'recipient', 'admin')
- created_at (DateTime)
```

### Donor Model
```python
- id (String, Primary Key)
- user_id (Foreign Key → User.id)
- blood_type (String)
- last_donation_date (DateTime)
- medical_conditions (Text)
- is_available (Boolean)
- status (String: 'pending', 'approved', 'rejected')
```

### BloodRequest Model
```python
- id (String, Primary Key)
- requester_id (Foreign Key → User.id)
- blood_type (String)
- quantity (Float)
- urgency (String)
- hospital (String)
- contact_number (String)
- notes (Text)
- request_date (DateTime)
- status (String: 'pending', 'approved', 'rejected')
```

### Donation Model
```python
- id (String, Primary Key)
- donor_id (Foreign Key → User.id)
- donation_date (DateTime)
- blood_type (String)
- quantity (Float)
- location (String)
- notes (Text)
```

### ContactMessage Model
```python
- id (String, Primary Key)
- name (String)
- email (String)
- phone (String)
- subject (String)
- message (Text)
- created_at (DateTime)
```

### Notification Model
```python
- id (String, Primary Key)
- user_id (Foreign Key → User.id)
- message (Text)
- created_at (DateTime)
```

## Frontend Forms & Endpoints

### 1. **Login Form** (`login.html`)
- **Form Fields**: Email, Password
- **Frontend Endpoints Called**:
  - `POST /api/auth/login` - Primary login endpoint
  - `POST /api/auth/firebase-login` - Firebase Google Sign-in (alternative)
  - `POST /verify_token` - Token verification for Firebase
  - `GET /api/auth/status` - Check authentication status
  - `POST /api/auth/logout` - Logout endpoint
- **Backend Connection**: ✅ **CONNECTED**
  - Routes: `/api/auth/login`, `/api/auth/firebase-login`, `/verify_token`, `/api/auth/status`, `/api/auth/logout`
  - User validation against database
  - JWT token generation
- **Database Connection**: ✅ **CONNECTED**
  - Queries User table for authentication
  - Stores session data in Flask-Session
  - Records login notifications in Notification table

### 2. **Registration Form** (`register.html`)
- **Form Fields**: Name, Email, Password, Role (Donor/Recipient), Blood Type (if Donor)
- **Frontend Endpoint Called**:
  - `POST /api/auth/register` - Registration endpoint
- **Backend Connection**: ✅ **CONNECTED**
  - Route: `/api/auth/register`
  - Password hashing using werkzeug
  - Role-based user creation
  - Auto-creates Donor record for donors with 'pending' status
- **Database Connection**: ✅ **CONNECTED**
  - Inserts into User table
  - Inserts into Donor table (if role='donor')
  - Creates welcome notification
  - Sends welcome email via SMTP

### 3. **Blood Request Form** (`Recipent.html`)
- **Form Fields**: Blood Type, Quantity, Urgency, Hospital, Contact Number, Notes
- **Frontend Endpoint Called**:
  - `POST /api/blood-requests` - Submit blood request
  - `GET /api/notifications` - Get request status notifications
- **Backend Connection**: ✅ **CONNECTED**
  - Route: `/api/blood-requests` (requires token authentication)
  - Creates BloodRequest record
  - Sends notification to requester
- **Database Connection**: ✅ **CONNECTED**
  - Inserts into BloodRequest table
  - Inserts into Notification table
  - Sends email notification to user

### 4. **Donation Form** (`dashboard.html`)
- **Form Fields**: Blood Type, Quantity, Location, Notes
- **Frontend Endpoint Called**:
  - `POST /api/donations` - Record donation
  - `GET /api/inventory` - Get blood inventory status
- **Backend Connection**: ✅ **CONNECTED**
  - Route: `/api/donations` (requires token authentication & donor role)
  - Creates Donation record
  - Updates Donor's last_donation_date
  - Sends thank you notification
- **Database Connection**: ✅ **CONNECTED**
  - Inserts into Donation table
  - Updates Donor table (last_donation_date)
  - Inserts into Notification table
  - Sends email notification to donor

### 5. **Contact Us Form** (`Contact Us.html`)
- **Form Fields**: Name, Email, Phone, Subject, Message
- **Frontend Endpoint Called**:
  - `POST /api/contact` - Submit contact message
- **Backend Connection**: ✅ **CONNECTED**
  - Route: `/api/contact` (public endpoint, no auth required)
  - Creates ContactMessage record
- **Database Connection**: ✅ **CONNECTED**
  - Inserts into ContactMessage table

### 6. **Admin Panel** (`adminPanel.html`)
- **Functions**: 
  - View pending donors
  - Approve/Reject donors
  - View pending blood requests
  - Approve/Reject blood requests
- **Frontend Endpoints Called**:
  - `GET /admin/pending-donors` - List pending donors
  - `PUT /admin/approve-donor/<donor_id>` - Approve donor
  - `DELETE /admin/reject-donor/<donor_id>` - Reject donor
  - `GET /admin/pending-requests` - List pending blood requests
  - `PUT /admin/approve-request/<request_id>` - Approve request
  - `DELETE /admin/reject-request/<request_id>` - Reject request
- **Backend Connection**: ✅ **CONNECTED**
  - Routes: `/admin/pending-donors`, `/admin/approve-donor/<id>`, `/admin/reject-donor/<id>`, etc.
  - All routes require admin role authentication
- **Database Connection**: ✅ **CONNECTED**
  - Queries Donor table (status filtering)
  - Updates Donor status
  - Queries BloodRequest table (status filtering)
  - Updates BloodRequest status
  - Creates notifications for approved/rejected items
  - Sends email notifications

## API Endpoints Summary

### Authentication Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | ✗ | Register new user |
| POST | `/api/auth/login` | ✗ | Login with email/password |
| POST | `/api/auth/firebase-login` | ✗ | Firebase Google Sign-in |
| POST | `/verify_token` | ✗ | Verify Firebase token |
| GET | `/api/auth/status` | ✓ | Check auth status |
| POST | `/api/auth/logout` | ✓ | Logout user |

### Donation Endpoints
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/api/donations` | ✓ | Donor | Create donation record |

### Blood Request Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/blood-requests` | ✓ | Submit blood request |

### Notification Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/notifications` | ✓ | Get user notifications |

### Contact Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/contact` | ✗ | Submit contact message |

### Admin Endpoints
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/admin/pending-donors` | ✓ | Admin | List pending donors |
| PUT | `/admin/approve-donor/<id>` | ✓ | Admin | Approve donor |
| DELETE | `/admin/reject-donor/<id>` | ✓ | Admin | Reject donor |
| GET | `/admin/pending-requests` | ✓ | Admin | List pending requests |
| PUT | `/admin/approve-request/<id>` | ✓ | Admin | Approve request |
| DELETE | `/admin/reject-request/<id>` | ✓ | Admin | Reject request |

### Inventory Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/inventory` | ✗ | Get blood inventory |

### Page Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | ✗ | Home page |
| GET | `/<name>.html` | ✗ | Render HTML templates |
| GET | `/dashboard` | ✓ | Donor/User dashboard |
| GET | `/about` | ✗ | About page |
| GET | `/adminPanel` | ✓ | Admin panel |
| GET | `/recipient` | ✓ | Recipient page |

## Connection Status: Frontend ↔ Backend ↔ Database

### ✅ FULLY CONNECTED & OPERATIONAL

**Login Form → Backend → Database**
- Frontend form sends credentials to `/api/auth/login`
- Backend validates against User table
- Returns JWT token & user data
- Status: ✅ WORKING

**Registration Form → Backend → Database**
- Frontend form submits data to `/api/auth/register`
- Backend hashes password & inserts into User table
- Creates Donor record if role='donor'
- Sends email notification
- Status: ✅ WORKING

**Blood Request Form → Backend → Database**
- Frontend form sends to `/api/blood-requests`
- Backend requires JWT authentication
- Inserts into BloodRequest table
- Creates notification & sends email
- Status: ✅ WORKING

**Donation Form → Backend → Database**
- Frontend form sends to `/api/donations`
- Backend validates donor role
- Inserts into Donation table
- Updates Donor's last_donation_date
- Creates notification & sends email
- Status: ✅ WORKING

**Contact Form → Backend → Database**
- Frontend form sends to `/api/contact`
- Backend inserts into ContactMessage table
- Status: ✅ WORKING

**Admin Panel → Backend → Database**
- Frontend queries `/admin/pending-donors`, `/admin/pending-requests`
- Backend filters by status from database
- Approve/Reject endpoints update status
- Creates notifications & sends emails
- Status: ✅ WORKING

## Notification System

All critical actions trigger notifications:
- User registration → Welcome notification
- Donation submitted → Thank you notification
- Blood request submitted → Confirmation notification
- Admin approval → Status change notification
- Admin rejection → Status change notification

Notifications are sent via:
1. **Database**: Stored in Notification table
2. **Email**: Sent via Gmail SMTP to user's email address
3. **Frontend**: Can be retrieved via `/api/notifications` endpoint

## Configuration

### Backend Configuration (`config.py`)
```python
SECRET_KEY = 'your-secret-key-here'
SQLALCHEMY_DATABASE_URI = 'sqlite:///blood_donation.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
```

### Environment Variables (`.env` or system env)
```
EMAIL_USER=your-gmail@gmail.com
EMAIL_PASS=your-app-password
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///blood_donation.db (optional, overrides config)
PORT=5000 (default)
```

### CORS Configuration
Allowed origins:
- `http://10.162.33.221:5500`
- `http://localhost:5500`

### Firebase Configuration
Firebase config loaded from `firebase_config.json` in Backend folder (optional, marked as optional in code)

## Running the Application

### Backend Setup
