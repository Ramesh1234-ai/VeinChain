# How to Check User Records in VeinChain

This guide shows all the methods available to retrieve and view user information in the VeinChain system.

---

## Method 1: Python Script (Direct Database Query)

### Using the Existing Script
The project already has a script to list all users:

**Location**: `Backend/scripts/list_users.py`

```python
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db, User

with app.app_context():
    users = User.query.with_entities(User.id, User.name, User.email).all()
    for u in users:
        print(u)
```

### How to Run It
```bash
cd Backend
python scripts/list_users.py
```

**Output Example**:
```
(UUID-12345, 'John Doe', 'john@example.com')
(UUID-67890, 'Jane Smith', 'jane@example.com')
```

---

## Method 2: Advanced Python Query - Get All User Details

### Query All Users with Full Details
Create a script or run in Python shell:

```python
# In Backend directory
from app import app
from database import db, User, Donor, BloodRequest, Donation

with app.app_context():
    # Get all users
    users = User.query.all()
    
    for user in users:
        print(f"\n{'='*50}")
        print(f"User ID: {user.id}")
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Created: {user.created_at}")
        
        # If user is a donor
        if user.role == 'donor':
            donor = Donor.query.filter_by(user_id=user.id).first()
            if donor:
                print(f"\n  Donor Info:")
                print(f"  - Blood Type: {donor.blood_type}")
                print(f"  - Status: {donor.status}")
                print(f"  - Available: {donor.is_available}")
                print(f"  - Last Donation: {donor.last_donation_date}")
                
                # Get donation history
                donations = Donation.query.filter_by(donor_id=user.id).all()
                print(f"  - Total Donations: {len(donations)}")
                for donation in donations:
                    print(f"    • {donation.donation_date} - {donation.quantity}ml {donation.blood_type}")
        
        # If user requested blood
        requests = BloodRequest.query.filter_by(requester_id=user.id).all()
        if requests:
            print(f"\n  Blood Requests: {len(requests)}")
            for req in requests:
                print(f"    • {req.request_date} - {req.quantity} units {req.blood_type} ({req.status})")
```

---

## Method 3: Query Specific User by Email

### Get a Single User's Record
```python
from app import app
from database import db, User

with app.app_context():
    # Query by email
    user = User.query.filter_by(email='john@example.com').first()
    
    if user:
        print(f"User Found:")
        print(f"ID: {user.id}")
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Created: {user.created_at}")
    else:
        print("User not found")
```

---

## Method 4: Query Users by Role

### Get All Donors
```python
from app import app
from database import db, User, Donor

with app.app_context():
    donors = User.query.filter_by(role='donor').all()
    
    print(f"Total Donors: {len(donors)}\n")
    for donor in donors:
        donor_info = Donor.query.filter_by(user_id=donor.id).first()
        print(f"Name: {donor.name}")
        print(f"Email: {donor.email}")
        print(f"Blood Type: {donor_info.blood_type if donor_info else 'N/A'}")
        print(f"Status: {donor_info.status if donor_info else 'N/A'}")
        print(f"Available: {donor_info.is_available if donor_info else 'N/A'}")
        print("-" * 40)
```

### Get All Recipients
```python
from app import app
from database import db, User

with app.app_context():
    recipients = User.query.filter_by(role='recipient').all()
    
    print(f"Total Recipients: {len(recipients)}\n")
    for recipient in recipients:
        print(f"Name: {recipient.name}")
        print(f"Email: {recipient.email}")
        print(f"Created: {recipient.created_at}")
        print("-" * 40)
```

### Get All Admins
```python
from app import app
from database import db, User

with app.app_context():
    admins = User.query.filter_by(role='admin').all()
    
    print(f"Total Admins: {len(admins)}\n")
    for admin in admins:
        print(f"Name: {admin.name}")
        print(f"Email: {admin.email}")
        print("-" * 40)
```

---

## Method 5: Query Donor Status

### Get Pending Donors (Awaiting Approval)
```python
from app import app
from database import db, User, Donor

with app.app_context():
    pending_donors = Donor.query.filter_by(status='pending').all()
    
    print(f"Pending Donor Approvals: {len(pending_donors)}\n")
    for donor in pending_donors:
        user = User.query.get(donor.user_id)
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"Blood Type: {donor.blood_type}")
        print(f"Waiting Since: {user.created_at}")
        print("-" * 40)
```

### Get Approved Donors
```python
from app import app
from database import db, User, Donor

with app.app_context():
    approved_donors = Donor.query.filter_by(status='approved').all()
    
    print(f"Approved Donors: {len(approved_donors)}\n")
    for donor in approved_donors:
        user = User.query.get(donor.user_id)
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"Blood Type: {donor.blood_type}")
        print(f"Available: {donor.is_available}")
        print(f"Last Donation: {donor.last_donation_date}")
        print("-" * 40)
```

---

## Method 6: View User Notifications

### Get Notifications for a Specific User
```python
from app import app
from database import db, User, Notification

with app.app_context():
    # Get user by email
    user = User.query.filter_by(email='john@example.com').first()
    
    if user:
        notifications = Notification.query.filter_by(user_id=user.id).order_by(
            Notification.created_at.desc()
        ).all()
        
        print(f"Notifications for {user.name}:\n")
        for notif in notifications:
            print(f"[{notif.created_at}] {notif.message}")
            print("-" * 40)
```

---

## Method 7: View Blood Requests

### Get All Blood Requests
```python
from app import app
from database import db, User, BloodRequest

with app.app_context():
    requests = BloodRequest.query.all()
    
    print(f"Total Blood Requests: {len(requests)}\n")
    for req in requests:
        user = User.query.get(req.requester_id)
        print(f"Requester: {user.name}")
        print(f"Email: {user.email}")
        print(f"Blood Type: {req.blood_type}")
        print(f"Quantity: {req.quantity} units")
        print(f"Urgency: {req.urgency}")
        print(f"Hospital: {req.hospital}")
        print(f"Status: {req.status}")
        print(f"Date: {req.request_date}")
        print("-" * 40)
```

### Get Pending Blood Requests (Only)
```python
from app import app
from database import db, User, BloodRequest

with app.app_context():
    pending = BloodRequest.query.filter_by(status='pending').all()
    
    print(f"Pending Blood Requests: {len(pending)}\n")
    for req in pending:
        user = User.query.get(req.requester_id)
        print(f"Requester: {user.name}")
        print(f"Needed: {req.quantity} units of {req.blood_type}")
        print(f"Hospital: {req.hospital}")
        print(f"Contact: {req.contact_number}")
        print("-" * 40)
```

---

## Method 8: View Donation History

### Get All Donations
```python
from app import app
from database import db, User, Donation

with app.app_context():
    donations = Donation.query.all()
    
    print(f"Total Donations: {len(donations)}\n")
    for donation in donations:
        donor = User.query.get(donation.donor_id)
        print(f"Donor: {donor.name}")
        print(f"Blood Type: {donation.blood_type}")
        print(f"Quantity: {donation.quantity}ml")
        print(f"Location: {donation.location}")
        print(f"Date: {donation.donation_date}")
        if donation.notes:
            print(f"Notes: {donation.notes}")
        print("-" * 40)
```

### Get Donations by Specific Donor
```python
from app import app
from database import db, User, Donation

with app.app_context():
    user = User.query.filter_by(email='john@example.com').first()
    
    if user:
        donations = Donation.query.filter_by(donor_id=user.id).all()
        
        print(f"Donation History for {user.name}:\n")
        print(f"Total Donations: {len(donations)}\n")
        for donation in donations:
            print(f"Date: {donation.donation_date}")
            print(f"Type: {donation.blood_type}")
            print(f"Quantity: {donation.quantity}ml")
            print(f"Location: {donation.location}")
            print("-" * 40)
```

---

## Method 9: Backend API Endpoints (Frontend)

### Check Auth Status
**Endpoint**: `GET /api/auth/status`

**JavaScript Example**:
```javascript
const token = localStorage.getItem('token');

fetch('http://localhost:5000/api/auth/status', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
.then(res => res.json())
.then(data => {
    if (data.logged_in) {
        console.log('Current User:', data.user);
        console.log('Name:', data.user.name);
        console.log('Email:', data.user.email);
        console.log('Role:', data.user.role);
    }
});
```

### Get User Notifications
**Endpoint**: `GET /api/notifications`

**JavaScript Example**:
```javascript
const token = localStorage.getItem('token');

fetch('http://localhost:5000/api/notifications', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
.then(res => res.json())
.then(notifications => {
    console.log('Your Notifications:');
    notifications.forEach(notif => {
        console.log(`[${notif.created_at}] ${notif.message}`);
    });
});
```

---

## Method 10: View Contact Messages

### Get All Contact Messages
```python
from app import app
from database import db, ContactMessage

with app.app_context():
    messages = ContactMessage.query.order_by(
        ContactMessage.created_at.desc()
    ).all()
    
    print(f"Total Contact Messages: {len(messages)}\n")
    for msg in messages:
        print(f"From: {msg.name} ({msg.email})")
        print(f"Phone: {msg.phone or 'N/A'}")
        print(f"Subject: {msg.subject or 'N/A'}")
        print(f"Message: {msg.message}")
        print(f"Date: {msg.created_at}")
        print("=" * 50)
```

---

## Method 11: Database Inspection (SQLite)

### Using SQLite Command Line
```bash
# Navigate to Backend directory
cd Backend

# Open SQLite database
sqlite3 instance/blood_donation.db

# List all users
sqlite> SELECT id, name, email, role, created_at FROM user;

# List all donors
sqlite> SELECT * FROM donor;

# List pending donors
sqlite> SELECT * FROM donor WHERE status = 'pending';

# List all blood requests
sqlite> SELECT * FROM blood_request;

# List pending blood requests
sqlite> SELECT * FROM blood_request WHERE status = 'pending';

# Count users by role
sqlite> SELECT role, COUNT(*) FROM user GROUP BY role;

# View user notifications
sqlite> SELECT * FROM notification ORDER BY created_at DESC;

# Exit SQLite
sqlite> .exit
```

---

## Method 12: Create a Comprehensive User Report Script

Save this as `Backend/scripts/user_report.py`:

```python
import os, sys
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db, User, Donor, BloodRequest, Donation, ContactMessage, Notification

def generate_user_report():
    with app.app_context():
        print("\n" + "=" * 60)
        print("VEINCHAIN USER RECORDS REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # User Statistics
        print("\n1. USER STATISTICS")
        print("-" * 60)
        total_users = User.query.count()
        admin_count = User.query.filter_by(role='admin').count()
        donor_count = User.query.filter_by(role='donor').count()
        recipient_count = User.query.filter_by(role='recipient').count()
        
        print(f"Total Users: {total_users}")
        print(f"  - Admins: {admin_count}")
        print(f"  - Donors: {donor_count}")
        print(f"  - Recipients: {recipient_count}")
        
        # Donor Statistics
        print("\n2. DONOR STATISTICS")
        print("-" * 60)
        approved_donors = Donor.query.filter_by(status='approved').count()
        pending_donors = Donor.query.filter_by(status='pending').count()
        rejected_donors = Donor.query.filter_by(status='rejected').count()
        
        print(f"Total Donors: {donor_count}")
        print(f"  - Approved: {approved_donors}")
        print(f"  - Pending Approval: {pending_donors}")
        print(f"  - Rejected: {rejected_donors}")
        
        # Blood Request Statistics
        print("\n3. BLOOD REQUEST STATISTICS")
        print("-" * 60)
        total_requests = BloodRequest.query.count()
        pending_requests = BloodRequest.query.filter_by(status='pending').count()
        approved_requests = BloodRequest.query.filter_by(status='approved').count()
        
        print(f"Total Blood Requests: {total_requests}")
        print(f"  - Pending: {pending_requests}")
        print(f"  - Approved: {approved_requests}")
        
        # Donation Statistics
        print("\n4. DONATION STATISTICS")
        print("-" * 60)
        total_donations = Donation.query.count()
        print(f"Total Donations Recorded: {total_donations}")
        
        # All Users Details
        print("\n5. ALL USERS DETAILED LIST")
        print("-" * 60)
        users = User.query.all()
        
        for user in users:
            print(f"\nUser: {user.name}")
            print(f"  Email: {user.email}")
            print(f"  Role: {user.role}")
            print(f"  Created: {user.created_at}")
            
            if user.role == 'donor':
                donor = Donor.query.filter_by(user_id=user.id).first()
                if donor:
                    donations = Donation.query.filter_by(donor_id=user.id).count()
                    print(f"  Blood Type: {donor.blood_type}")
                    print(f"  Status: {donor.status}")
                    print(f"  Available: {donor.is_available}")
                    print(f"  Total Donations: {donations}")
                    print(f"  Last Donation: {donor.last_donation_date}")
            
            requests = BloodRequest.query.filter_by(requester_id=user.id).count()
            if requests > 0:
                print(f"  Blood Requests: {requests}")
        
        # Contact Messages
        print("\n6. RECENT CONTACT MESSAGES")
        print("-" * 60)
        messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
        for msg in messages:
            print(f"\nFrom: {msg.name} ({msg.email})")
            print(f"Subject: {msg.subject or 'No Subject'}")
            print(f"Date: {msg.created_at}")
            print(f"Message: {msg.message[:100]}...")
        
        print("\n" + "=" * 60)
        print("END OF REPORT")
        print("=" * 60 + "\n")

if __name__ == '__main__':
    generate_user_report()
```

**Run it with**:
```bash
cd Backend
python scripts/user_report.py
```

---

## Summary: Quick Commands

| Task | Command |
|------|---------|
| List all users | `python scripts/list_users.py` |
| Generate full report | `python scripts/user_report.py` |
| Open database | `sqlite3 instance/blood_donation.db` |
| View users in SQLite | `SELECT * FROM user;` |
| View donors in SQLite | `SELECT * FROM donor;` |
| View pending donors | `SELECT * FROM donor WHERE status='pending';` |
| View blood requests | `SELECT * FROM blood_request;` |
| Check auth (from frontend) | `GET /api/auth/status` + token |
| View notifications (from frontend) | `GET /api/notifications` + token |

---

## Best Practices for Checking User Records

1. **Use Python Scripts** - Best for complex queries and reports
2. **Use SQLite CLI** - Best for quick ad-hoc queries
3. **Use Backend Endpoints** - Best for production applications and API integration
4. **Use Frontend** - Best for end-user viewing of their own data

---

**Last Updated**: January 9, 2026
**VeinChain Blood Donation Management System**
