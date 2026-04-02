# VeinChain System Architecture & Connection Diagrams

## 🏗️ Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VEINCHAIN SYSTEM                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    FRONTEND (HTML/CSS/JavaScript)                   │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │  Login   │  │Register  │  │ Blood    │  │Donation │           │   │
│  │  │  Form    │  │  Form    │  │Request   │  │  Form   │           │   │
│  │  │          │  │          │  │          │  │         │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────────┐  │   │
│  │  │ Contact  │  │Admin     │  │   Dashboard & Navigation         │  │   │
│  │  │  Form    │  │ Panel    │  │   (Notifications, Inventory)     │  │   │
│  │  │          │  │          │  │                                  │  │   │
│  │  └──────────┘  └──────────┘  └──────────────────────────────────┘  │   │
│  │                                                                      │   │
│  │                     Fetch API (JSON over HTTPS)                     │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                             ↓ HTTP Requests                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                  BACKEND (Flask - Python)                           │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │              API ENDPOINTS                                  │   │   │
│  │  ├─────────────────────────────────────────────────────────────┤   │   │
│  │  │  POST   /api/auth/register      [Validation, Hashing]      │   │   │
│  │  │  POST   /api/auth/login         [JWT Token Generation]      │   │   │
│  │  │  POST   /api/blood-requests     [Record + Notification]     │   │   │
│  │  │  POST   /api/donations          [Record + Update Donor]     │   │   │
│  │  │  POST   /api/contact            [Save Message]              │   │   │
│  │  │  GET    /admin/pending-donors   [Query with Filters]        │   │   │
│  │  │  PUT    /admin/approve-donor    [Update Status + Notify]    │   │   │
│  │  │  DELETE /admin/reject-donor     [Update Status + Notify]    │   │   │
│  │  │  GET    /admin/pending-requests [Query with Filters]        │   │   │
│  │  │  PUT    /admin/approve-request  [Update Status + Notify]    │   │   │
│  │  │  DELETE /admin/reject-request   [Update Status + Notify]    │   │   │
│  │  │  GET    /api/notifications      [User-specific Query]       │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │              AUTHENTICATION & AUTHORIZATION                 │   │   │
│  │  ├─────────────────────────────────────────────────────────────┤   │   │
│  │  │  JWT Token Validation      [Authorization: Bearer <token>]  │   │   │
│  │  │  Role-Based Access Control [@role_required decorator]       │   │   │
│  │  │  Password Hashing          [werkzeug.security]              │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │                    SQLAlchemy ORM                                    │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                          ↓ Database Queries                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │              DATABASE (SQLite - blood_donation.db)                  │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐            │   │
│  │  │ User Table  │  │ Donor Table  │  │BloodRequest │            │   │
│  │  │             │  │              │  │   Table     │            │   │
│  │  │ • id        │  │ • id         │  │ • id        │            │   │
│  │  │ • name      │  │ • user_id-→ │  │ • request_id│            │   │
│  │  │ • email     │  │ • blood_type │  │ • blood_type│            │   │
│  │  │ • password  │  │ • status ★  │  │ • quantity  │            │   │
│  │  │ • role ★    │  │ • created_at │  │ • status ★  │            │   │
│  │  │             │  │              │  │ • created_at│            │   │
│  │  └─────────────┘  └──────────────┘  └──────────────┘            │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐     │   │
│  │  │Donation Table│  │ ContactMessage  │  │Notification Tbl  │     │   │
│  │  │              │  │      Table      │  │                  │     │   │
│  │  │ • id         │  │ • id            │  │ • id             │     │   │
│  │  │ • donor_id-→ │  │ • name          │  │ • user_id-→     │     │   │
│  │  │ • blood_type │  │ • email         │  │ • message        │     │   │
│  │  │ • quantity   │  │ • message       │  │ • created_at     │     │   │
│  │  │ • created_at │  │ • created_at    │  │                  │     │   │
│  │  │              │  │                 │  │                  │     │   │
│  │  └──────────────┘  └─────────────────┘  └──────────────────┘     │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                       ↓ Email Sending                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │              EMAIL SERVICE (Gmail SMTP)                             │   │
│  │  • Welcome emails on registration                                  │   │
│  │  • Confirmation emails on donations                                │   │
│  │  • Notifications on blood requests                                 │   │
│  │  • Approval/Rejection notifications                                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ★ = Critical for role-based access & status tracking                       │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```
---
## 🔄 Form Submission Workflow Diagrams

### 1. LOGIN FORM FLOW

```
┌────────────────────┐
│  User fills form   │
│  Email + Password  │
└────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ Frontend Validates Input               │
│ • Email format check                   │
│ • Password length check                │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────────┐
│ POST /api/auth/login                                           │
│ { email: "user@example.com", password: "password123" }         │
└────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Backend Processing                                              │
│ 1. Query User table: filter_by(email=email)                     │
│ 2. Check password hash: check_password_hash()                   │
│ 3. Generate JWT token (24-hour expiration)                      │
│ 4. Return { token, user_data }                                  │
└─────────────────────────────────────────────────────────────────┘
         ↓
    ┌────────┴────────┐
    ↓                 ↓
  Valid         Invalid
    │             │
    ↓             ↓
┌─────────┐   ┌─────────────┐
│ Token + │   │ Error 401   │
│ User    │   │ "Invalid    │
│ Data    │   │ credentials"│
└────┬────┘   └─────────────┘
     ↓
┌──────────────────────────────────────┐
│ Frontend Actions                     │
│ • Store token in localStorage        │
│ • Store user data in localStorage    │
│ • Redirect based on role             │
└──────────────────────────────────────┘
```

---

### 2. REGISTRATION FORM FLOW

```
┌────────────────────────────────────────┐
│ User fills registration form           │
│ • Name, Email, Password, Role          │
│ • Blood Type (if Donor)                │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────┐
│ Frontend Validates                             │
│ • All required fields                          │
│ • Email format                                 │
│ • Password strength (min 6 chars)              │
└────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ POST /api/auth/register                                     │
│ { name, email, password, role, blood_type }                 │
└─────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ Backend Processing - Database Operations                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Database Transaction Begin                                  │
│  ├─ CHECK: Email unique? → User.query.filter_by(email)      │
│  ├─ HASH: password → generate_password_hash()               │
│  ├─ INSERT: User table                                       │
│  │   • id: UUID generated                                    │
│  │   • name, email, password_hash, role                      │
│  │   • created_at: NOW()                                     │
│  │                                                           │
│  ├─ IF role == 'donor':                                      │
│  │   INSERT: Donor table                                     │
│  │   • id: UUID                                              │
│  │   • user_id: FK → User.id                                 │
│  │   • blood_type: from form                                 │
│  │   • status: 'pending' (awaits admin approval)             │
│  │                                                           │
│  ├─ INSERT: Notification table                               │
│  │   • message: "Welcome {name}! Registered as {role}"       │
│  │                                                           │
│  └─ SEND: Email via Gmail SMTP                               │
│     • To: user@example.com                                   │
│     • Subject: "Blood.Ninja Welcome"                         │
│     • Body: Welcome message                                  │
│  Database Transaction Commit                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
         ↓
    ┌────────┴────────┐
    ↓                 ↓
Success           Error
  │                 │
  ↓                 ↓
┌──────────────┐  ┌──────────────────┐
│ Return 201   │  │ Return 400/500   │
│ User Created │  │ Error Message    │
└────┬─────────┘  └──────────────────┘
     ↓
┌──────────────────────────────────────┐
│ Frontend Actions                     │
│ • Show success message               │
│ • Redirect to login page             │
└──────────────────────────────────────┘
     ↓
┌──────────────────────────────────────┐
│ Email Arrives in User's Inbox        │
│ "Welcome to VeinChain!"              │
└──────────────────────────────────────┘
```

---

### 3. BLOOD REQUEST FORM FLOW

```
┌────────────────────────────────────────┐
│ Logged-in Recipient fills form         │
│ • Blood Type, Quantity, Urgency        │
│ • Hospital, Contact Number, Notes      │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ Frontend Attaches JWT Token                                │
│ Authorization: Bearer <token_from_localStorage>            │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────┐
│ POST /api/blood-requests                               │
│ Headers: Authorization Bearer token                    │
│ Body: { blood_type, quantity, urgency, ... }           │
└────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ Backend Token Validation                                    │
│ ├─ Decode JWT token                                        │
│ ├─ Extract user_id from token                              │
│ ├─ Query User table → Get current_user                     │
│ └─ Continue if valid, reject if invalid                    │
└─────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ Backend Processing - Database Operations                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Database Transaction Begin                                  │
│  ├─ INSERT: BloodRequest table                               │
│  │   • id: UUID                                              │
│  │   • requester_id: user_id (from JWT)                      │
│  │   • blood_type, quantity, urgency, hospital, etc.         │
│  │   • status: 'pending'                                     │
│  │   • request_date: NOW()                                   │
│  │                                                           │
│  ├─ INSERT: Notification table                               │
│  │   • user_id: requester_id                                 │
│  │   • message: "Request for {qty} units {blood_type}"       │
│  │   • created_at: NOW()                                     │
│  │                                                           │
│  └─ SEND: Email via Gmail SMTP                               │
│     • To: user.email (from User table)                       │
│     • Subject: "Blood Request Submitted"                     │
│     • Body: Request details                                  │
│  Database Transaction Commit                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Return 201 Created                 │
│ { message: "Request created" }     │
└────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ Frontend Actions                     │
│ • Show success message               │
│ • Fetch /api/notifications           │
│ • Display notifications              │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ Admin Dashboard Shows New Request    │
│ /admin/pending-requests ← updated    │
└──────────────────────────────────────┘
         ↓
    ┌────────┴────────┐
    ↓                 ↓
 Approved         Rejected
    │                 │
    ↓                 ↓
┌──────────────┐  ┌──────────────┐
│UPDATE status │  │UPDATE status │
│= 'approved'  │  │= 'rejected'  │
│Send Email    │  │Send Email    │
└──────────────┘  └──────────────┘
```

---

### 4. DONATION FORM FLOW

```
┌────────────────────────────────────────┐
│ Logged-in Donor fills form             │
│ • Blood Type, Quantity, Location       │
│ • Notes (optional)                     │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ Frontend Attaches JWT Token                                │
│ Authorization: Bearer <token_from_localStorage>            │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────┐
│ POST /api/donations                                    │
│ Headers: Authorization Bearer token                    │
│ Body: { blood_type, quantity, location, notes }        │
└────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ Backend Token & Role Validation                             │
│ ├─ Decode JWT token                                        │
│ ├─ Extract user_id from token                              │
│ ├─ Query User table → Get current_user                     │
│ ├─ CHECK: current_user.role == 'donor'?                    │
│ └─ Reject if not a donor (403 Forbidden)                   │
└─────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ Backend Processing - Database Operations                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Database Transaction Begin                                  │
│  ├─ INSERT: Donation table                                   │
│  │   • id: UUID                                              │
│  │   • donor_id: user_id (from JWT)                          │
│  │   • donation_date: NOW()                                  │
│  │   • blood_type, quantity, location, notes                 │
│  │                                                           │
│  ├─ UPDATE: Donor table                                      │
│  │   • donor_id: user_id                                     │
│  │   • last_donation_date: NOW()                             │
│  │                                                           │
│  ├─ INSERT: Notification table                               │
│  │   • user_id: donor_id                                     │
│  │   • message: "Thanks! {qty}ml {blood_type} recorded"      │
│  │   • created_at: NOW()                                     │
│  │                                                           │
│  └─ SEND: Email via Gmail SMTP                               │
│     • To: user.email                                         │
│     • Subject: "Donation Confirmed"                          │
│     • Body: Thank you message with details                   │
│  Database Transaction Commit                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Return 201 Created                 │
│ { message: "Donation recorded" }   │
└────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ Frontend Actions                     │
│ • Show thank you message             │
│ • Fetch /api/inventory               │
│ • Update inventory display           │
│ • Fetch /api/notifications           │
│ • Show notification                  │
└──────────────────────────────────────┘
```

---

## 👤 Role-Based Access Control Flow

```
┌─────────────────────────────────────────┐
│ User Logs In                            │
│ POST /api/auth/login                    │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│ Backend Returns JWT Token with Role                 │
│ { token, user: { id, email, role } }                │
└─────────────────────────────────────────────────────┘
         ↓
         ┌─────────────────────────────────────────────┐
         │ role = ?                                    │
         └────┬──────────┬──────────┬──────────────────┘
              │          │          │
         ┌────▼──┐  ┌───▼──┐  ┌───▼────┐
         │ admin │  │donor │  │recipent│
         └────┬──┘  └───┬──┘  └───┬────┘
              │         │         │
    ┌─────────▼─┐  ┌────▼─────┐  ┌─▼────────────┐
    │Can Access:│  │Can Access:│  │Can Access:  │
    │           │  │           │  │             │
    │• /admin/* │  │• /api/    │  │• /api/      │
    │  (Approve)│  │  donations│  │  blood-    │
    │           │  │• /        │  │  requests   │
    │• /api/auth│  │  dashboard│  │• /Recipent  │
    │• /api/    │  │• /api/    │  │  .html      │
    │  notif... │  │  inventory│  │• /api/      │
    │           │  │• /api/    │  │  notif...   │
    │           │  │  notif... │  │             │
    └───────────┘  └───────────┘  └─────────────┘
```
---
## 🔐 Authentication & Token Flow
```
┌──────────────────────────────────────────────────────────┐
│ User Login Request                                       │
│ POST /api/auth/login                                     │
│ { email, password }                                      │
└──────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────┐
│ Backend                                                  │
│ 1. Query User by email                                   │
│ 2. Hash incoming password                                │
│ 3. Compare with stored hash                              │
│ 4. If match:                                             │
│    • Generate JWT token                                  │
│    • Token contains: user_id, email, exp (24hrs)         │
│    • Sign with SECRET_KEY                                │
└──────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────┐
│ Return to Frontend                                       │
│ {                                                        │
│   token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",   │
│   user: { id, email, name, role }                        │
│ }                                                        │
└──────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────┐
│ Frontend                                                 │
│ localStorage.setItem('token', token)                     │
└──────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────┐
│ Subsequent Protected Request                             │
│ GET /api/notifications                                   │
│ Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..   │
└──────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────┐
│ Backend @token_required Decorator                        │
│ 1. Extract token from Authorization header               │
│ 2. Decode token with SECRET_KEY                          │
│ 3. Extract user_id from decoded token                    │
│ 4. Query User by user_id                                 │
│ 5. Pass user object to route handler                     │
│ 6. If token invalid/expired → 401 Unauthorized           │
└──────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────┐
│ Route Handler Executes                                   │
│ current_user = User(id, name, email, role)               │
│ Process request with user context                        │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Database Relationship Diagram
```
┌───────────────────┐
│   User Table      │
├───────────────────┤
│ id (PK)           │◄──────────────┐
│ name              │               │
│ email (UNIQUE)    │               │
│ password_hash     │               │
│ role              │               │
│ created_at        │               │
└───────────────────┘               │
         ▲                           │
         │                    ┌──────┴─────────┬──────────┐
         │                    │                │          │
         │                    ↓                ↓          ↓
    ┌────────────────┐  ┌───────────────┐ ┌──────────┐ ┌──────────────┐
    │ Notification   │  │ Donor Table   │ │Donation  │ │BloodRequest  │
    │  Table         │  │               │ │ Table    │ │ Table        │
    ├────────────────┤  ├───────────────┤ ├──────────┤ ├──────────────┤
    │ id (PK)        │  │ id (PK)       │ │ id (PK)  │ │ id (PK)      │
    │ user_id (FK)───┤  │ user_id (FK)──┤ │ donor_id │ │requester_id  │
    │ message        │  │ blood_type    │ │(FK)──┐   │ │(FK)──────┐   │
    │ created_at     │  │ status        │ │      │   │ │         │   │
    └────────────────┘  │ last_donation │ │ blood│   │ │ blood_  │   │
                        │ _date         │ │ type │   │ │ type    │   │
                        │ is_available  │ │      │   │ │         │   │
                        │ created_at    │ │ qty  │   │ │ qty     │   │
                        └───────────────┘ │      │   │ │         │   │
                                          │locat │   │ │hospital │   │
                        ┌──────────────┐  │ion   │   │ │         │   │
                        │ Contact      │  │      │   │ │urgency  │   │
                        │ Message      │  │date  │   │ │         │   │
                        │ Table        │  │status│   │ │status   │   │
                        ├──────────────┤  │created│   │ │created  │   │
                        │ id (PK)      │  │_at   │   │ │_at      │   │
                        │ name         │  └──────┘   │ │         │   │
                        │ email        │             │ │ notes   │   │
                        │ phone        │             │ └─────────┘   │
                        │ subject      │               └──────────────┘
                        │ message      │
                        │ created_at   │
                        └──────────────┘

        Key:
        ─── Relationship
        (PK) Primary Key
        (FK) Foreign Key
        ──┤ One-to-Many
```
---
## 🔄 Admin Approval Workflow

```
┌─────────────────────────────────────────────┐
│ Donor Registration                          │
│ /api/auth/register → role='donor'           │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│ Donor record created with status='pending'  │
│ (User can login but cannot donate yet)      │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ Admin sees pending donor in Admin Panel                 │
│ GET /admin/pending-donors                               │
│ [Donor not yet approved]                                │
└─────────────────────────────────────────────────────────┘
         ↓
    ┌─────────┴─────────┐
    ↓                   ↓
┌─────────────┐   ┌─────────────┐
│ APPROVE     │   │ REJECT      │
└──────┬──────┘   └──────┬──────┘
       │                 │
       ↓                 ↓
┌──────────────────┐  ┌──────────────────┐
│PUT /admin/       │  │DELETE /admin/    │
│approve-donor/id  │  │reject-donor/id   │
│                  │  │                  │
│Updates:          │  │Updates:          │
│status='approved' │  │status='rejected' │
│                  │  │                  │
│Creates:          │  │Creates:          │
│Notification      │  │Notification      │
│Sends Email       │  │Sends Email       │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         ↓                     ↓
    ┌────────────┐        ┌─────────────┐
    │ Donor can  │        │Donor cannot │
    │ donate now │        │ donate ever │
    └────────────┘        └─────────────┘
         ↓
    Notifications &
    Email sent to
    donor's email
```

---

## 🚀 Complete Request-Response Cycle Example

```
                            VEINCHAIN REQUEST LIFECYCLE

User Action              Frontend              Network           Backend              Database         Email
    │                       │                    │                 │                   │                │
    │                       │                    │                 │                   │                │
 User fills           ┌─────▼──────┐            │                 │                   │                │
 registration         │ Validate   │            │                 │                   │                │
 form                 │ input data │            │                 │                   │                │
    │                 └─────┬──────┘            │                 │                   │                │
    │                       │                    │                 │                   │                │
    │                  ┌────▼────────┐          │                 │                   │                │
    │                  │ POST /api/   │         │                 │                   │                │
    │                  │auth/register │────────▶│                 │                   │                │
    │                  │ {data}       │         │                 │                   │                │
    │                  └──────────────┘         │           ┌─────▼──────┐           │                │
    │                       │                    │           │ Check email│           │                │
    │                       │                    │           │ is unique  │           │                │
    │                       │                    │           └─────┬──────┘           │                │
    │                       │                    │                 │                   │                │
    │                       │                    │           ┌─────▼──────┐           │                │
    │                       │                    │           │ Hash pwd   │           │                │
    │                       │                    │           └─────┬──────┘           │                │
    │                       │                    │                 │                   │                │
    │                       │                    │           ┌─────▼──────────────┐   │                │
    │                       │                    │           │ INSERT User record │───▶│ User table     │
    │                       │                    │           └─────┬──────────────┘   │ created        │
    │                       │                    │                 │                   │                │
    │                       │                    │           ┌─────▼──────────────┐   │                │
    │                       │                    │           │ INSERT Donor record│───▶│ Donor table    │
    │                       │                    │           └─────┬──────────────┘   │ created        │
    │                       │                    │                 │                   │ status=pending │
    │                       │                    │           ┌─────▼────────────────┐ │                │
    │                       │                    │           │CREATE Notification  │──▶│ Notification   │
    │                       │                    │           └─────┬────────────────┘ │ table          │
    │                       │                    │                 │                   │                │
    │                       │                    │           ┌─────▼─────────────────────────────┐     │
    │                       │                    │           │ SEND EMAIL (Gmail SMTP)           │────▶│ Welcome email
    │                       │                    │           │ To: user@example.com              │     │ sent
    │                       │                    │           │ Subject: Welcome to VeinChain     │     │
    │                       │                    │           │ Body: Welcome message             │     │
    │                       │                    │           └─────┬─────────────────────────────┘     │
    │                       │                    │                 │                   │                │
    │                       │                    │     ┌───────────▼──────────┐        │                │
    │                       │                    │     │ RETURN 201 Created   │        │                │
    │                       │                    │     │ { message: "...",    │        │                │
    │                       │                    │     │   user: {...} }      │        │                │
    │                       │                    │     └──────────┬───────────┘        │                │
    │                       │◀─────────────────────────────────────┘                    │                │
    │                  ┌────▼──────────┐                                               │                │
    │                  │Store token in │                                               │                │
    │                  │localStorage   │                                               │                │
    │                  └────┬──────────┘                                               │                │
    │                       │                                                          │                │
    │                  ┌────▼──────────┐                                               │                │
    │                  │Show success   │                                               │                │
    │                  │message        │                                               │                │
    │                  └────┬──────────┘                                               │                │
    │                       │                                                          │                │
    │                  ┌────▼──────────┐                                               │                │
    │                  │Redirect to    │                                               │                │
    │                  │login page     │                                               │                │
    │                  └───────────────┘                                               │                │
    │                       │                                                          │                │
   Awaits                 Email                                                        │        Email arrives
   login                  arrives                                                      │         in inbox
                                                                                       │
```
---
This comprehensive architecture shows how all components of VeinChain work together:
- **Frontend** collects user input
- **Backend** validates and processes requests
- **Database** stores all data
- **Email** notifies users
- **Authentication** secures the system
- **Authorization** controls access by role
---
*All systems operational as of January 9, 2026*
