# VeinChain - Quick Commands to Check User Records

## 🚀 Fastest Ways to Check Records

### 1. Run Existing Script (1 minute)
```bash
cd c:\Users\DELL\Desktop\VeinChain\Backend
python scripts/list_users.py
```
**Shows**: All user IDs, names, emails

---

### 2. Generate Full Report (2 minutes)
Create `Backend/scripts/user_report.py` and run:
```bash
cd Backend
python scripts/user_report.py
```
**Shows**: 
- User statistics
- Donor statistics  
- Blood request statistics
- All users with details
- Recent contact messages

---

### 3. SQLite Database Query (Immediate)
```bash
cd c:\Users\DELL\Desktop\VeinChain\Backend
sqlite3 instance/blood_donation.db

# Common queries:
sqlite> SELECT id, name, email, role FROM user;
sqlite> SELECT * FROM donor;
sqlite> SELECT * FROM blood_request WHERE status='pending';
sqlite> SELECT * FROM donation;
sqlite> .exit
```

---

## 📋 Useful SQL Queries for SQLite

### View All Users
```sql
SELECT id, name, email, role, created_at FROM user;
```

### View Only Donors
```sql
SELECT id, name, email FROM user WHERE role='donor';
```

### View Only Recipients
```sql
SELECT id, name, email FROM user WHERE role='recipient';
```

### View Only Admins
```sql
SELECT id, name, email FROM user WHERE role='admin';
```

### View Donor Details
```sql
SELECT u.name, u.email, d.blood_type, d.status, d.is_available 
FROM user u 
JOIN donor d ON u.id = d.user_id;
```

### View Pending Donors (Awaiting Approval)
```sql
SELECT u.name, u.email, d.blood_type 
FROM donor d 
JOIN user u ON d.user_id = u.id 
WHERE d.status = 'pending';
```

### View Approved Donors
```sql
SELECT u.name, u.email, d.blood_type, d.last_donation_date 
FROM donor d 
JOIN user u ON d.user_id = u.id 
WHERE d.status = 'approved';
```

### View All Blood Requests
```sql
SELECT u.name, u.email, br.blood_type, br.quantity, br.urgency, br.status 
FROM blood_request br 
JOIN user u ON br.requester_id = u.id 
ORDER BY br.request_date DESC;
```

### View Pending Blood Requests
```sql
SELECT u.name, u.email, br.blood_type, br.quantity, br.hospital 
FROM blood_request br 
JOIN user u ON br.requester_id = u.id 
WHERE br.status = 'pending';
```

### View User's Donation History
```sql
SELECT donation_date, blood_type, quantity, location 
FROM donation 
WHERE donor_id = 'USER_ID_HERE' 
ORDER BY donation_date DESC;
```

### View User's Blood Requests
```sql
SELECT request_date, blood_type, quantity, urgency, status 
FROM blood_request 
WHERE requester_id = 'USER_ID_HERE' 
ORDER BY request_date DESC;
```

### View User's Notifications
```sql
SELECT message, created_at FROM notification 
WHERE user_id = 'USER_ID_HERE' 
ORDER BY created_at DESC;
```

### View Contact Messages
```sql
SELECT name, email, subject, message, created_at 
FROM contact_message 
ORDER BY created_at DESC;
```

### Count Users by Role
```sql
SELECT role, COUNT(*) as count FROM user GROUP BY role;
```

### Count Donors by Status
```sql
SELECT status, COUNT(*) as count FROM donor GROUP BY status;
```

### Count Blood Requests by Status
```sql
SELECT status, COUNT(*) as count FROM blood_request GROUP BY status;
```

### Total Donations by Blood Type
```sql
SELECT blood_type, COUNT(*) as count, SUM(quantity) as total_units 
FROM donation 
GROUP BY blood_type;
```

---

## 🐍 Python Commands for Interactive Checking

### Open Python Shell and Query
```bash
cd Backend
python
```

Then in Python:
```python
from app import app
from database import db, User, Donor, BloodRequest, Donation

with app.app_context():
    # Get all users
    users = User.query.all()
    for u in users:
        print(f"{u.name} - {u.email} - {u.role}")
    
    # Get specific user
    user = User.query.filter_by(email='john@example.com').first()
    print(user.name if user else "Not found")
    
    # Get all donors
    donors = User.query.filter_by(role='donor').all()
    print(f"Total donors: {len(donors)}")
    
    # Get pending donors
    pending = Donor.query.filter_by(status='pending').all()
    print(f"Pending approvals: {len(pending)}")
```

---

## 🌐 Frontend API Methods (JavaScript)

### Check Current User
```javascript
fetch('http://localhost:5000/api/auth/status', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
})
.then(r => r.json())
.then(data => console.log(data.user));
```

### Get My Notifications
```javascript
fetch('http://localhost:5000/api/notifications', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
})
.then(r => r.json())
.then(notifs => console.log(notifs));
```

### Get Blood Inventory
```javascript
fetch('http://localhost:5000/api/inventory')
.then(r => r.json())
.then(inventory => console.log(inventory));
```

---

## 📊 Data Structure Reference

### User Table Columns
- `id` - UUID primary key
- `name` - User's full name
- `email` - Email address (unique)
- `password` - Hashed password
- `role` - 'admin', 'donor', or 'recipient'
- `created_at` - Registration timestamp

### Donor Table Columns
- `id` - UUID
- `user_id` - Foreign key to User
- `blood_type` - A+, A-, B+, B-, O+, O-, AB+, AB-
- `status` - 'pending', 'approved', 'rejected'
- `is_available` - True/False
- `last_donation_date` - Last donation timestamp

### BloodRequest Table Columns
- `id` - UUID
- `requester_id` - Foreign key to User
- `blood_type` - Blood type requested
- `quantity` - Units needed
- `urgency` - 'low', 'medium', 'high'
- `hospital` - Hospital name
- `contact_number` - Phone number
- `status` - 'pending', 'approved', 'rejected'
- `request_date` - When request was made

### Donation Table Columns
- `id` - UUID
- `donor_id` - Foreign key to User
- `donation_date` - When donated
- `blood_type` - Blood type donated
- `quantity` - Amount in ml
- `location` - Where donated
- `notes` - Any notes

---

## ⚡ One-Liner Commands

### Count total users
```bash
sqlite3 c:\Users\DELL\Desktop\VeinChain\Backend\instance\blood_donation.db "SELECT COUNT(*) FROM user;"
```

### List all emails
```bash
sqlite3 c:\Users\DELL\Desktop\VeinChain\Backend\instance\blood_donation.db "SELECT name, email FROM user;"
```

### Count pending donors
```bash
sqlite3 c:\Users\DELL\Desktop\VeinChain\Backend\instance\blood_donation.db "SELECT COUNT(*) FROM donor WHERE status='pending';"
```

### Count pending blood requests
```bash
sqlite3 c:\Users\DELL\Desktop\VeinChain\Backend\instance\blood_donation.db "SELECT COUNT(*) FROM blood_request WHERE status='pending';"
```

---

## 📁 Database Location
**Path**: `c:\Users\DELL\Desktop\VeinChain\Backend\instance\blood_donation.db`

**Opens with**:
- SQLite (command line): `sqlite3`
- DB Browser for SQLite (GUI): https://sqlitebrowser.org/
- VS Code SQLite extension

---

## 🎯 Troubleshooting

**Error: "Unable to open database file"**
- Make sure you're in the Backend directory
- Database auto-creates on first Flask run

**Error: "No such table"**
- Run Flask app first: `python app.py`
- Flask auto-creates tables on startup

**Error: "ModuleNotFoundError"**
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in the Backend directory

---

## 💡 Tips

1. **For regular checking** → Use SQLite commands (fastest)
2. **For detailed reports** → Use Python scripts
3. **For live user data** → Use API endpoints in frontend
4. **For monitoring** → Create custom dashboard endpoint

---

**Last Updated**: January 9, 2026
**VeinChain Blood Donation Management System**
