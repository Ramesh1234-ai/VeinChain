#!/bin/bash
# VeinChain Database Initialization Script
# Run this script to set up the database for deployment

set -e

echo "🔧 VeinChain Database Setup"
echo "=============================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to Backend directory
cd "$(dirname "$0")"

echo -e "${YELLOW}Step 1: Installing dependencies...${NC}"
pip install -q Flask Flask-SQLAlchemy Flask-Migrate python-dotenv psycopg2-binary

echo -e "${GREEN}✓ Dependencies installed${NC}"

echo -e "${YELLOW}Step 2: Creating database tables...${NC}"

python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✓ Database tables created successfully')
"

echo -e "${YELLOW}Step 3: Verifying database schema...${NC}"

python -c "
from models import app, db
from models import User, Donor, BloodRequest, Donation, Notification, ContactMessage

with app.app_context():
    # Check tables exist
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    expected_tables = ['user', 'donor', 'blood_request', 'donation', 'notification', 'contact_message']
    for table in expected_tables:
        if table in tables:
            print(f'✓ {table} table exists')
        else:
            print(f'✗ {table} table missing!')
            exit(1)
"

echo -e "${GREEN}✓ Database schema verified${NC}"

echo ""
echo -e "${GREEN}=============================="
echo "✓ Database setup complete!"
echo "=============================${NC}"
echo ""
echo "You can now run the application with:"
echo "  python app.py"
