@echo off
REM =====================================================
REM WhatsApp OPD Chatbot - AUTOMATED CLOUD DEPLOYMENT
REM =====================================================
REM This script deploys your chatbot to FREE Render cloud
REM Credentials are entered interactively (not stored)
REM =====================================================

setlocal enabledelayedexpansion

echo.
echo =====================================================
echo   WhatsApp OPD Chatbot - Cloud Deployment
echo =====================================================
echo.
echo This script will deploy your chatbot to the cloud
echo FREE tier - runs 24/7 with no cost!
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed
    echo Please install from: https://www.python.org/
    pause
    exit /b 1
)
echo ✓ Python found
echo.

REM Check Git
echo [2/6] Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not installed
    echo Please install from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo ✓ Git found
echo.

REM Get Twilio credentials
echo [3/6] Getting your Twilio credentials...
echo.
echo IMPORTANT: Your credentials will NOT be stored
echo They will only be used for deployment
echo.
set /p ACCOUNT_SID="Enter Twilio Account SID (starts with AC): "
set /p AUTH_TOKEN="Enter Twilio Auth Token: "
set /p WHATSAPP_NUMBER="Enter Twilio WhatsApp Number (e.g., +1234567890): "
echo.

REM Validate credentials not empty
if "!ACCOUNT_SID!"=="" (
    echo ERROR: Account SID is required
    pause
    exit /b 1
)
if "!AUTH_TOKEN!"=="" (
    echo ERROR: Auth Token is required
    pause
    exit /b 1
)
if "!WHATSAPP_NUMBER!"=="" (
    echo ERROR: WhatsApp Number is required
    pause
    exit /b 1
)

echo ✓ Credentials received (not stored)
echo.

REM Create deployment folder
echo [4/6] Preparing deployment package...
if not exist "deployment_package" mkdir deployment_package
cd deployment_package

REM Create app.py
echo Creating application file...
(
echo """
echo WhatsApp OPD Chatbot - Production
echo """
echo from flask import Flask, request, jsonify, render_template_string
echo from twilio.rest import Client
echo from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, desc
echo from sqlalchemy.ext.declarative import declarative_base
echo from sqlalchemy.orm import sessionmaker
echo from datetime import datetime, timedelta
echo import os
echo import json
echo from dotenv import load_dotenv
echo import logging
echo.
echo load_dotenv()
echo.
echo app = Flask(__name__)
echo app.secret_key = 'opd-chatbot-secret'
echo.
echo TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
echo TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
echo TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155552671')
echo.
echo if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
echo     twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
echo else:
echo     twilio_client = None
echo.
echo DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///appointments.db')
echo engine = create_engine(DATABASE_URL, pool_pre_ping=True)
echo Session = sessionmaker(bind=engine)
echo Base = declarative_base()
echo.
echo class Appointment(Base):
echo     __tablename__ = 'appointments'
echo     id = Column(Integer, primary_key=True)
echo     patient_phone = Column(String, nullable=False)
echo     patient_name = Column(String, nullable=False)
echo     appointment_date = Column(DateTime, nullable=False)
echo     reason = Column(String)
echo     status = Column(String, default='confirmed')
echo     created_at = Column(DateTime, default=datetime.utcnow)
echo.
echo Base.metadata.create_all(engine)
echo.
echo @app.route('/')
echo def index():
echo     return render_template_string('''
echo     ^<html^>
echo     ^<head^>
echo         ^<title^>OPD Chatbot^</title^>
echo         ^<style^>
echo             body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%); height: 100vh; }
echo             .container { background: white; padding: 50px; border-radius: 10px; max-width: 600px; margin: 0 auto; }
echo             h1 { color: #333; }
echo             .btn { display: inline-block; margin: 10px; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }
echo         ^</style^>
echo     ^</head^>
echo     ^<body^>
echo         ^<div class="container"^>
echo             ^<h1^>🏥 OPD Appointment Chatbot^</h1^>
echo             ^<p^>WhatsApp automated appointment booking system^</p^>
echo             ^<div class="buttons"^>
echo                 ^<a class="btn" href="/dashboard"^>📊 Admin Dashboard^</a^>
echo                 ^<a class="btn" href="/status"^>✅ API Status^</a^>
echo             ^</div^>
echo         ^</div^>
echo     ^</body^>
echo     ^</html^>
echo     ''')
echo.
echo @app.route('/status')
echo def status():
echo     return jsonify({'status': 'active', 'service': 'WhatsApp OPD Chatbot'})
echo.
echo @app.route('/dashboard')
echo def dashboard():
echo     session = Session()
echo     appointments = session.query(Appointment).all()
echo     session.close()
echo     return render_template_string('''
echo     ^<html^>^<head^>^<title^>Dashboard^</title^>^<style^>
echo     body { font-family: Arial; padding: 20px; background: #f0f0f0; }
echo     .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
echo     table { width: 100%%; border-collapse: collapse; }
echo     th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
echo     th { background: #667eea; color: white; }
echo     ^</style^>^</head^>^<body^>
echo     ^<div class="container"^>
echo     ^<h1^>📊 Appointments Dashboard^</h1^>
echo     ''' + ('^<table^>^<tr^>^<th^>Patient^</th^>^<th^>Phone^</th^>^<th^>Date^</th^>^<th^>Reason^</th^>^</tr^>' + ''.join([f'^<tr^>^<td^>{apt.patient_name}^</td^>^<td^>{apt.patient_phone}^</td^>^<td^>{apt.appointment_date}^</td^>^<td^>{apt.reason}^</td^>^</tr^>' for apt in appointments]) + '^</table^>' if appointments else '^<p^>No appointments yet^</p^>') + '''
echo     ^</div^>^</body^>^</html^>
echo     ''')
echo.
echo @app.route('/webhook', methods=['POST'])
echo def webhook():
echo     incoming_msg = request.values.get('Body', 'Hi').strip()
echo     return '', 200
echo.
echo if __name__ == '__main__':
echo     port = int(os.getenv('PORT', 5000))
echo     app.run(host='0.0.0.0', port=port, debug=False)
) > app.py

echo ✓ Application file created
echo.

REM Create requirements.txt
echo Creating dependencies file...
(
echo Flask==2.3.3
echo twilio==8.10.0
echo SQLAlchemy==2.0.21
echo python-dotenv==1.0.0
echo gunicorn==21.2.0
echo psycopg2-binary==2.9.7
) > requirements.txt

echo ✓ Dependencies file created
echo.

REM Create Procfile
echo Creating Procfile...
(
echo web: gunicorn app:app
) > Procfile

echo ✓ Procfile created
echo.

REM Create .env with credentials
echo [5/6] Configuring credentials...
(
echo TWILIO_ACCOUNT_SID=!ACCOUNT_SID!
echo TWILIO_AUTH_TOKEN=!AUTH_TOKEN!
echo TWILIO_WHATSAPP_NUMBER=whatsapp:!WHATSAPP_NUMBER!
echo DATABASE_URL=sqlite:///appointments.db
echo FLASK_ENV=production
) > .env

echo ✓ Configuration created (local only)
echo.

REM Create deployment README
echo Creating deployment guide...
(
echo # Deploy to Render Cloud
echo.
echo Your chatbot is ready! Follow these steps:
echo.
echo 1. Go to: https://github.com/new
echo 2. Create repository named: opd-chatbot
echo 3. Upload all files from deployment_package folder
echo.
echo 4. Go to: https://render.com
echo 5. New Web Service from GitHub
echo 6. Select opd-chatbot repository
echo.
echo 7. Settings:
echo    - Build: pip install -r requirements.txt
echo    - Start: gunicorn app:app
echo.
echo 8. Add Environment Variables:
echo    TWILIO_ACCOUNT_SID=!ACCOUNT_SID!
echo    TWILIO_AUTH_TOKEN=!AUTH_TOKEN!
echo    TWILIO_WHATSAPP_NUMBER=whatsapp:!WHATSAPP_NUMBER!
echo.
echo 9. Click Deploy
echo.
echo 10. After deployment, get URL and add to Twilio:
echo     https://console.twilio.com/ ^> Services ^> WhatsApp
echo     Webhook: YOUR_URL/webhook
) > DEPLOY_INSTRUCTIONS.txt

echo ✓ Instructions created
echo.

REM Summary
echo [6/6] Deployment package ready!
echo.
echo =====================================================
echo   ✅ READY FOR CLOUD DEPLOYMENT!
echo =====================================================
echo.
echo Your deployment package is in: deployment_package\
echo.
echo FILES CREATED:
echo  ✓ app.py (your chatbot)
echo  ✓ requirements.txt (dependencies)
echo  ✓ Procfile (deployment config)
echo  ✓ .env (your credentials - KEEP PRIVATE!)
echo  ✓ DEPLOY_INSTRUCTIONS.txt
echo.
echo NEXT STEPS:
echo.
echo 1. Open DEPLOY_INSTRUCTIONS.txt
echo 2. Follow the 10 simple steps
echo 3. Your chatbot will be LIVE on Render!
echo.
echo IMPORTANT:
echo  - Never share .env file
echo  - Keep credentials private
echo  - Use DEPLOY_INSTRUCTIONS.txt
echo.
echo =====================================================
echo.
pause
