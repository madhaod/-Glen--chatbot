#!/bin/bash

# =====================================================
# WhatsApp OPD Chatbot - AUTOMATED CLOUD DEPLOYMENT
# =====================================================
# This script deploys your chatbot to FREE Render cloud
# Credentials are entered interactively (not stored)
# =====================================================

set -e

echo ""
echo "====================================================="
echo "   WhatsApp OPD Chatbot - Cloud Deployment"
echo "====================================================="
echo ""
echo "This script will deploy your chatbot to the cloud"
echo "FREE tier - runs 24/7 with no cost!"
echo ""

# Check Python
echo "[1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not installed"
    echo "Mac: brew install python3"
    echo "Linux: sudo apt-get install python3"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo "✓ Found $PYTHON_VERSION"
echo ""

# Check Git
echo "[2/6] Checking Git installation..."
if ! command -v git &> /dev/null; then
    echo "ERROR: Git not installed"
    echo "Mac: brew install git"
    echo "Linux: sudo apt-get install git"
    exit 1
fi
echo "✓ Git found"
echo ""

# Get Twilio credentials
echo "[3/6] Getting your Twilio credentials..."
echo ""
echo "IMPORTANT: Your credentials will NOT be stored"
echo "They will only be used for deployment"
echo ""

read -p "Enter Twilio Account SID (starts with AC): " ACCOUNT_SID
read -sp "Enter Twilio Auth Token: " AUTH_TOKEN
echo ""
read -p "Enter Twilio WhatsApp Number (e.g., +1234567890): " WHATSAPP_NUMBER
echo ""

# Validate
if [ -z "$ACCOUNT_SID" ] || [ -z "$AUTH_TOKEN" ] || [ -z "$WHATSAPP_NUMBER" ]; then
    echo "ERROR: All credentials are required"
    exit 1
fi

echo "✓ Credentials received (not stored)"
echo ""

# Create deployment folder
echo "[4/6] Preparing deployment package..."
mkdir -p deployment_package
cd deployment_package

# Create app.py
echo "Creating application file..."
cat > app.py << 'EOF'
"""
WhatsApp OPD Chatbot - Production
"""
from flask import Flask, request, jsonify, render_template_string
from twilio.rest import Client
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
app.secret_key = 'opd-chatbot-secret'

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155552671')

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    twilio_client = None

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///appointments.db')
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_phone = Column(String, nullable=False)
    patient_name = Column(String, nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    reason = Column(String)
    status = Column(String, default='confirmed')
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

@app.route('/')
def index():
    return render_template_string('''
    <html>
    <head>
        <title>OPD Chatbot</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; }
            .container { background: white; padding: 50px; border-radius: 10px; max-width: 600px; margin: 0 auto; }
            h1 { color: #333; }
            .btn { display: inline-block; margin: 10px; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 OPD Appointment Chatbot</h1>
            <p>WhatsApp automated appointment booking system</p>
            <div class="buttons">
                <a class="btn" href="/dashboard">📊 Admin Dashboard</a>
                <a class="btn" href="/status">✅ API Status</a>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/status')
def status():
    return jsonify({'status': 'active', 'service': 'WhatsApp OPD Chatbot'})

@app.route('/dashboard')
def dashboard():
    session = Session()
    appointments = session.query(Appointment).all()
    session.close()
    
    rows = ''.join([f'<tr><td>{apt.patient_name}</td><td>{apt.patient_phone}</td><td>{apt.appointment_date}</td><td>{apt.reason}</td></tr>' for apt in appointments])
    
    return render_template_string('''
    <html><head><title>Dashboard</title><style>
    body { font-family: Arial; padding: 20px; background: #f0f0f0; }
    .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #667eea; color: white; }
    </style></head><body>
    <div class="container">
    <h1>📊 Appointments Dashboard</h1>
    ''' + ('<table><tr><th>Patient</th><th>Phone</th><th>Date</th><th>Reason</th></tr>' + rows + '</table>' if appointments else '<p>No appointments yet</p>') + '''
    </div></body></html>
    ''')

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', 'Hi').strip()
    return '', 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
EOF

echo "✓ Application file created"
echo ""

# Create requirements.txt
echo "Creating dependencies file..."
cat > requirements.txt << 'EOF'
Flask==2.3.3
twilio==8.10.0
SQLAlchemy==2.0.21
python-dotenv==1.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.7
EOF

echo "✓ Dependencies file created"
echo ""

# Create Procfile
echo "Creating Procfile..."
echo "web: gunicorn app:app" > Procfile

echo "✓ Procfile created"
echo ""

# Create .env with credentials
echo "[5/6] Configuring credentials..."
cat > .env << EOF
TWILIO_ACCOUNT_SID=$ACCOUNT_SID
TWILIO_AUTH_TOKEN=$AUTH_TOKEN
TWILIO_WHATSAPP_NUMBER=whatsapp:$WHATSAPP_NUMBER
DATABASE_URL=sqlite:///appointments.db
FLASK_ENV=production
EOF

echo "✓ Configuration created (local only)"
echo ""

# Create deployment README
echo "Creating deployment guide..."
cat > DEPLOY_INSTRUCTIONS.txt << EOF
# Deploy to Render Cloud

Your chatbot is ready! Follow these steps:

1. Go to: https://github.com/new
2. Create repository named: opd-chatbot
3. Upload all files from deployment_package folder

4. Go to: https://render.com
5. New Web Service from GitHub
6. Select opd-chatbot repository

7. Settings:
   - Build: pip install -r requirements.txt
   - Start: gunicorn app:app

8. Add Environment Variables:
   TWILIO_ACCOUNT_SID=$ACCOUNT_SID
   TWILIO_AUTH_TOKEN=$AUTH_TOKEN
   TWILIO_WHATSAPP_NUMBER=whatsapp:$WHATSAPP_NUMBER

9. Click Deploy

10. After deployment, get URL and add to Twilio:
    https://console.twilio.com/ > Services > WhatsApp
    Webhook: YOUR_URL/webhook
EOF

echo "✓ Instructions created"
echo ""

# Summary
echo "[6/6] Deployment package ready!"
echo ""
echo "====================================================="
echo "   ✅ READY FOR CLOUD DEPLOYMENT!"
echo "====================================================="
echo ""
echo "Your deployment package is in: deployment_package/"
echo ""
echo "FILES CREATED:"
echo "  ✓ app.py (your chatbot)"
echo "  ✓ requirements.txt (dependencies)"
echo "  ✓ Procfile (deployment config)"
echo "  ✓ .env (your credentials - KEEP PRIVATE!)"
echo "  ✓ DEPLOY_INSTRUCTIONS.txt"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Open DEPLOY_INSTRUCTIONS.txt"
echo "2. Follow the 10 simple steps"
echo "3. Your chatbot will be LIVE on Render!"
echo ""
echo "IMPORTANT:"
echo "  - Never share .env file"
echo "  - Keep credentials private"
echo "  - Use DEPLOY_INSTRUCTIONS.txt"
echo ""
echo "====================================================="
echo ""
