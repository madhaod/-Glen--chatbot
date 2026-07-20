"""
WhatsApp OPD Patient Appointment Booking Chatbot - PRODUCTION VERSION
With Admin Dashboard for managing appointments
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155552671')

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    twilio_client = None

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///appointments.db')
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# ==================== DATABASE MODELS ====================

class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String)
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    patient_phone = Column(String, nullable=False)
    patient_name = Column(String, nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    reason = Column(String)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_phone': self.patient_phone,
            'patient_name': self.patient_name,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ConversationState(Base):
    __tablename__ = 'conversation_states'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True, nullable=False)
    current_step = Column(String, default='greeting')
    session_data = Column(Text, default='{}')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(engine)

# ==================== APPOINTMENT SLOTS ====================

AVAILABLE_SLOTS = {
    'Monday': ['09:00', '09:30', '10:00', '10:30', '11:00', '14:00', '14:30', '15:00', '15:30'],
    'Tuesday': ['09:00', '09:30', '10:00', '10:30', '11:00', '14:00', '14:30', '15:00', '15:30'],
    'Wednesday': ['09:00', '09:30', '10:00', '10:30', '11:00', '14:00', '14:30', '15:00', '15:30'],
    'Thursday': ['09:00', '09:30', '10:00', '10:30', '11:00', '14:00', '14:30', '15:00', '15:30'],
    'Friday': ['09:00', '09:30', '10:00', '10:30', '11:00', '14:00', '14:30', '15:00', '15:30'],
    'Saturday': ['09:00', '10:00', '11:00'],
}

# ==================== HELPER FUNCTIONS ====================

def get_session_data(phone_number):
    session = Session()
    conv_state = session.query(ConversationState).filter_by(phone_number=phone_number).first()
    
    if not conv_state:
        conv_state = ConversationState(phone_number=phone_number, current_step='greeting', session_data='{}')
        session.add(conv_state)
        session.commit()
    
    session.close()
    return conv_state

def update_session_data(phone_number, step, data=None):
    session = Session()
    conv_state = session.query(ConversationState).filter_by(phone_number=phone_number).first()
    
    if conv_state:
        conv_state.current_step = step
        if data:
            conv_state.session_data = json.dumps(data)
        conv_state.updated_at = datetime.utcnow()
        session.commit()
    
    session.close()

def get_next_7_days():
    dates = []
    today = datetime.now()
    for i in range(1, 8):
        future_date = today + timedelta(days=i)
        dates.append(future_date.strftime('%Y-%m-%d'))
    return dates

def send_whatsapp_message(to_number, message):
    if not twilio_client:
        logger.warning("Twilio not configured. Skipping message send.")
        return False
    try:
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f'whatsapp:{to_number}',
            body=message
        )
        return True
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return False

def parse_session_data(session_data_json):
    try:
        return json.loads(session_data_json) if session_data_json else {}
    except:
        return {}

# ==================== CHATBOT LOGIC ====================

def handle_greeting(phone_number):
    message = """👋 Welcome to OPD Appointment Booking System!

I'm here to help you book an appointment with our clinic. Please reply with your name to get started."""
    update_session_data(phone_number, 'name')
    return message

def handle_name(phone_number, user_message):
    session = Session()
    patient = session.query(Patient).filter_by(phone_number=phone_number).first()
    if not patient:
        patient = Patient(phone_number=phone_number, name=user_message.strip())
        session.add(patient)
    else:
        patient.name = user_message.strip()
    session.commit()
    session.close()
    
    session_data = {'name': user_message.strip()}
    update_session_data(phone_number, 'date', session_data)
    
    dates = get_next_7_days()
    date_options = '\n'.join([f"{i+1}. {date}" for i, date in enumerate(dates)])
    
    message = f"""👤 Great! Hello {user_message.strip()}!

📅 Please select your preferred appointment date:
{date_options}

Reply with the number of your preferred date."""
    
    return message

def handle_date(phone_number, user_message):
    try:
        date_index = int(user_message.strip()) - 1
        dates = get_next_7_days()
        
        if 0 <= date_index < len(dates):
            selected_date = dates[date_index]
            day_name = datetime.strptime(selected_date, '%Y-%m-%d').strftime('%A')
            
            session_data = {'date': selected_date, 'day_name': day_name}
            update_session_data(phone_number, 'time', session_data)
            
            slots = AVAILABLE_SLOTS.get(day_name, [])
            slots_text = '\n'.join([f"{i+1}. {slot}" for i, slot in enumerate(slots)])
            
            message = f"""✅ Date selected: {selected_date} ({day_name})

⏰ Please select your preferred time slot:
{slots_text}

Reply with the number of your preferred slot."""
            
            return message
        else:
            return "❌ Invalid selection. Please reply with a number between 1 and 7."
    except ValueError:
        return "❌ Invalid input. Please reply with a number (1-7)."

def handle_time(phone_number, user_message):
    conv_state = get_session_data(phone_number)
    session_data = parse_session_data(conv_state.session_data)
    
    try:
        time_index = int(user_message.strip()) - 1
        day_name = session_data.get('day_name')
        slots = AVAILABLE_SLOTS.get(day_name, [])
        
        if 0 <= time_index < len(slots):
            selected_time = slots[time_index]
            session_data['time'] = selected_time
            update_session_data(phone_number, 'reason', session_data)
            
            message = """📝 Please describe the reason for your visit (e.g., General Checkup, Fever, Chest Pain, etc.)"""
            return message
        else:
            return f"❌ Invalid selection. Please reply with a number between 1 and {len(slots)}."
    except ValueError:
        return "❌ Invalid input. Please reply with a number."

def handle_reason(phone_number, user_message):
    conv_state = get_session_data(phone_number)
    session_data = parse_session_data(conv_state.session_data)
    
    session_data['reason'] = user_message.strip()
    update_session_data(phone_number, 'confirm', session_data)
    
    date = session_data.get('date')
    time = session_data.get('time')
    reason = session_data.get('reason')
    name = session_data.get('name')
    
    message = f"""📋 Please confirm your appointment details:

👤 Name: {name}
📅 Date: {date}
⏰ Time: {time}
🏥 Reason: {reason}

Reply with:
✅ YES to confirm
❌ NO to modify"""
    
    return message

def handle_confirmation(phone_number, user_message):
    user_input = user_message.strip().upper()
    
    if user_input in ['YES', 'Y', '✅']:
        session = Session()
        conv_state = get_session_data(phone_number)
        session_data = parse_session_data(conv_state.session_data)
        
        appointment = Appointment(
            patient_phone=phone_number,
            patient_name=session_data.get('name'),
            appointment_date=f"{session_data.get('date')} {session_data.get('time')}",
            reason=session_data.get('reason'),
            status='confirmed'
        )
        session.add(appointment)
        session.commit()
        session.close()
        
        update_session_data(phone_number, 'greeting', {})
        
        message = f"""✅ Appointment Confirmed!

Your appointment has been successfully booked.
📞 You will receive a reminder notification 24 hours before your appointment.

Thank you for using our service! 🙏"""
        
        return message
    
    elif user_input in ['NO', 'N', '❌']:
        update_session_data(phone_number, 'greeting', {})
        return handle_greeting(phone_number)
    
    else:
        return "Please reply with YES or NO to confirm your appointment."

# ==================== WEBHOOK ROUTE ====================

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '').replace('whatsapp:', '')
        
        conv_state = get_session_data(from_number)
        current_step = conv_state.current_step
        
        if current_step == 'greeting':
            response_msg = handle_greeting(from_number)
        elif current_step == 'name':
            response_msg = handle_name(from_number, incoming_msg)
        elif current_step == 'date':
            response_msg = handle_date(from_number, incoming_msg)
        elif current_step == 'time':
            response_msg = handle_time(from_number, incoming_msg)
        elif current_step == 'reason':
            response_msg = handle_reason(from_number, incoming_msg)
        elif current_step == 'confirm':
            response_msg = handle_confirmation(from_number, incoming_msg)
        else:
            response_msg = handle_greeting(from_number)
        
        send_whatsapp_message(from_number, response_msg)
        return '', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return '', 500

# ==================== API ROUTES ====================

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    session = Session()
    appointments = session.query(Appointment).filter_by(status='confirmed').order_by(desc(Appointment.appointment_date)).all()
    result = [apt.to_dict() for apt in appointments]
    session.close()
    return jsonify(result), 200

@app.route('/api/appointments/today', methods=['GET'])
def get_today_appointments():
    session = Session()
    today = datetime.now().date()
    
    appointments = session.query(Appointment).filter(
        Appointment.appointment_date >= datetime.combine(today, datetime.min.time()),
        Appointment.appointment_date <= datetime.combine(today, datetime.max.time()),
        Appointment.status == 'confirmed'
    ).order_by(Appointment.appointment_date).all()
    
    result = [apt.to_dict() for apt in appointments]
    session.close()
    return jsonify(result), 200

@app.route('/api/appointments/<int:apt_id>', methods=['DELETE'])
def cancel_appointment(apt_id):
    session = Session()
    appointment = session.query(Appointment).filter_by(id=apt_id).first()
    
    if appointment:
        appointment.status = 'cancelled'
        session.commit()
        session.close()
        return jsonify({'message': 'Appointment cancelled'}), 200
    
    session.close()
    return jsonify({'error': 'Appointment not found'}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    session = Session()
    total = session.query(Appointment).count()
    confirmed = session.query(Appointment).filter_by(status='confirmed').count()
    cancelled = session.query(Appointment).filter_by(status='cancelled').count()
    patients = session.query(Patient).count()
    
    session.close()
    return jsonify({
        'total_appointments': total,
        'confirmed': confirmed,
        'cancelled': cancelled,
        'total_patients': patients
    }), 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'active', 'service': 'WhatsApp OPD Chatbot'}), 200

# ==================== ADMIN DASHBOARD ====================

ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OPD Appointment Manager - Admin Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 14px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-card h3 {
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .stat-number {
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .main-content {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .section-title {
            font-size: 24px;
            color: #333;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #667eea;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
        }
        
        .tab-button {
            padding: 12px 25px;
            background: #f0f0f0;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .tab-button.active {
            background: #667eea;
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        thead {
            background: #f8f9fa;
        }
        
        th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #e0e0e0;
        }
        
        td {
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        tbody tr:hover {
            background: #f8f9fa;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status-confirmed {
            background: #d4edda;
            color: #155724;
        }
        
        .status-pending {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-cancelled {
            background: #f8d7da;
            color: #721c24;
        }
        
        .btn-delete {
            background: #dc3545;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.3s ease;
        }
        
        .btn-delete:hover {
            background: #c82333;
        }
        
        .btn-refresh {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 20px;
            transition: background 0.3s ease;
        }
        
        .btn-refresh:hover {
            background: #5568d3;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        
        .filter-section {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .filter-section input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            
            .tabs {
                flex-wrap: wrap;
            }
            
            table {
                font-size: 12px;
            }
            
            th, td {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 OPD Appointment Manager</h1>
            <p>WhatsApp Appointment Booking System - Admin Dashboard</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Appointments</h3>
                <div class="stat-number" id="stat-total">0</div>
            </div>
            <div class="stat-card">
                <h3>Confirmed</h3>
                <div class="stat-number" id="stat-confirmed">0</div>
            </div>
            <div class="stat-card">
                <h3>Cancelled</h3>
                <div class="stat-number" id="stat-cancelled">0</div>
            </div>
            <div class="stat-card">
                <h3>Total Patients</h3>
                <div class="stat-number" id="stat-patients">0</div>
            </div>
        </div>
        
        <div class="main-content">
            <h2 class="section-title">📋 Appointments</h2>
            
            <button class="btn-refresh" onclick="loadData()">🔄 Refresh Data</button>
            
            <div class="filter-section">
                <input type="text" id="searchInput" placeholder="Search by patient name or phone..." onkeyup="filterAppointments()">
            </div>
            
            <div class="tabs">
                <button class="tab-button active" onclick="switchTab('all')">All Appointments</button>
                <button class="tab-button" onclick="switchTab('today')">Today's Appointments</button>
            </div>
            
            <div id="all" class="tab-content active">
                <div id="all-content" class="loading">Loading...</div>
            </div>
            
            <div id="today" class="tab-content">
                <div id="today-content" class="loading">Loading...</div>
            </div>
        </div>
    </div>
    
    <script>
        async function loadData() {
            try {
                // Load stats
                const statsResponse = await fetch('/api/stats');
                const stats = await statsResponse.json();
                document.getElementById('stat-total').textContent = stats.total_appointments;
                document.getElementById('stat-confirmed').textContent = stats.confirmed;
                document.getElementById('stat-cancelled').textContent = stats.cancelled;
                document.getElementById('stat-patients').textContent = stats.total_patients;
                
                // Load all appointments
                const appointmentsResponse = await fetch('/api/appointments');
                const appointments = await appointmentsResponse.json();
                displayAppointments(appointments, 'all-content');
                
                // Load today's appointments
                const todayResponse = await fetch('/api/appointments/today');
                const todayAppointments = await todayResponse.json();
                displayAppointments(todayAppointments, 'today-content');
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('all-content').innerHTML = '<div class="empty-state">❌ Error loading appointments</div>';
            }
        }
        
        function displayAppointments(appointments, elementId) {
            const container = document.getElementById(elementId);
            
            if (!appointments || appointments.length === 0) {
                container.innerHTML = '<div class="empty-state">📭 No appointments found</div>';
                return;
            }
            
            let html = `
                <table>
                    <thead>
                        <tr>
                            <th>Patient Name</th>
                            <th>Phone</th>
                            <th>Date & Time</th>
                            <th>Reason</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            appointments.forEach(apt => {
                const date = new Date(apt.appointment_date);
                const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                const statusClass = `status-${apt.status}`;
                
                html += `
                    <tr>
                        <td>${apt.patient_name}</td>
                        <td>${apt.patient_phone}</td>
                        <td>${formattedDate}</td>
                        <td>${apt.reason || 'N/A'}</td>
                        <td><span class="status-badge ${statusClass}">${apt.status.toUpperCase()}</span></td>
                        <td>
                            ${apt.status === 'confirmed' ? `<button class="btn-delete" onclick="deleteAppointment(${apt.id})">Cancel</button>` : '-'}
                        </td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }
        
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        async function deleteAppointment(id) {
            if (confirm('Are you sure you want to cancel this appointment?')) {
                try {
                    const response = await fetch(`/api/appointments/${id}`, { method: 'DELETE' });
                    if (response.ok) {
                        alert('Appointment cancelled successfully');
                        loadData();
                    }
                } catch (error) {
                    alert('Error cancelling appointment');
                }
            }
        }
        
        function filterAppointments() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const rows = document.querySelectorAll('table tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }
        
        // Load data when page loads
        loadData();
        
        // Auto-refresh every 30 seconds
        setInterval(loadData, 30000);
    </script>
</body>
</html>
"""

@app.route('/dashboard')
def dashboard():
    return render_template_string(ADMIN_DASHBOARD_HTML)

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OPD Chatbot</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; display: flex; justify-content: center; align-items: center; }
            .container { background: white; padding: 50px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            p { color: #666; }
            .buttons { margin-top: 30px; }
            a { display: inline-block; margin: 10px; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }
            a:hover { background: #5568d3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 OPD Appointment Chatbot</h1>
            <p>WhatsApp automated appointment booking system</p>
            <div class="buttons">
                <a href="/dashboard">📊 Admin Dashboard</a>
                <a href="/status">✅ API Status</a>
            </div>
        </div>
    </body>
    </html>
    """)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
