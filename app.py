from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mail import Mail, Message
import uuid
from datetime import datetime
import qrcode
from io import BytesIO
import base64
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'


def init_db():
    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()
    # Drop the existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS events")
    cursor.execute("DROP TABLE IF EXISTS participation")

    # Create the users table
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # Create the events table with tickets_sold column
    cursor.execute('''
    CREATE TABLE events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        date TEXT NOT NULL,
        occupancy INTEGER NOT NULL,
        tickets_sold INTEGER DEFAULT 0,
        creator_id INTEGER NOT NULL,
        FOREIGN KEY (creator_id) REFERENCES users (id)
    )
    ''')

    # Create the participation table
    cursor.execute('''
    CREATE TABLE participation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    ''')

    conn.commit()
    conn.close()



# Call init_db to initialize the database
init_db()

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'buvangamer845@gmail.com'
app.config['MAIL_PASSWORD'] = 'oegtuulkfhpjtabq'  # Use App-specific password from Google
mail = Mail(app)

# Sample in-memory data storage
users = {}
user_events = {"registered": 2, "created": 1}
events = [
    {"name": "Tech Conference 2024", "location": "New York", "date": "2024-05-12", "occupancy": 500},
    {"name": "Music Festival", "location": "Los Angeles", "date": "2024-06-20", "occupancy": 3000},
    {"name": "Art Expo", "location": "Chicago", "date": "2024-07-15", "occupancy": 200}
]

def generate_ticket_number():
    return f"SBS-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8]}"

def generate_qr_code(ticket_number):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(ticket_number)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64 string
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def send_event_confirmation_email(email, event_details):
    ticket_number = generate_ticket_number()
    qr_code = generate_qr_code(ticket_number)
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
            <h1 style="color: #333;">SBS Event Services</h1>
            <h2>Event Ticket Confirmation</h2>
        </div>
        <div style="padding: 20px;">
            <h3>Event Details:</h3>
            <p><strong>Event Name:</strong> {event_details['name']}</p>
            <p><strong>Date:</strong> {event_details['date']}</p>
            <p><strong>Location:</strong> {event_details['location']}</p>
            <p><strong>Ticket Number:</strong> {ticket_number}</p>
            <div style="text-align: center; margin: 20px 0;">
                <img src="data:image/png;base64,{qr_code}" alt="QR Code" style="max-width: 200px;"/>
            </div>
            <hr>
            <p style="font-size: 12px; color: #666;">
                This ticket is non-transferable and must be presented at the event entrance.
                For any queries, please contact support@sbsevents.com
            </p>
        </div>
    </body>
    </html>
    """
    
    msg = Message(
        subject=f"Your Ticket for {event_details['name']} - SBS Event Services",
        sender='buvangamer845@gmail.com',
        recipients=[email]
    )
    msg.html = html_content
    mail.send(msg)
    return ticket_number

@app.route('/process_event_registration', methods=['POST'])
def process_event_registration():
    try:
        data = request.get_json()
        event_name = data.get('event_name')
        email = data.get('email')

        # Check if the event exists
        cursor = init_db().cursor()
        cursor.execute("SELECT id FROM events WHERE name = ?", (event_name,))
        event = cursor.fetchone()
        if not event:
            return jsonify({'success': False, 'message': 'Event not found'})

        # Register the user to the event
        cursor.execute("INSERT INTO participation (user_id, event_id) VALUES (?, ?)", (user_id, event[0]))
        init_db().commit()

        # Generate a ticket number (simple mockup)
        ticket_number = 'TICKET123'
        return jsonify({'success': True, 'ticket_number': ticket_number})

    except Exception as e:
        print("Error in processing event registration:", e)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)  # Encrypt password

        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Registration successful! You can now log in.")
            conn.close()  # Close connection here

            # Redirect to login after successful registration
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()  # Ensure connection is closed on error
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/home', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, stored_password = user
            if check_password_hash(stored_password, password):  # Verify encrypted password
                session['username'] = username
                session['user_id'] = user_id
                flash("Login successful!")
                return redirect(url_for('home'))
            else:
                flash("Incorrect password. Please try again.")
        else:
            flash("Username not found. Please register.")

        return redirect(url_for('login'))
    
    elif 'username' in session:
        return render_template('home.html', events=events)
    else:
        return redirect(url_for('login'))



@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chatbot_response', methods=['POST'])
def chatbot_response():
    data = request.json
    user_message = data.get("message", "")
    bot_response = rule_based_response(user_message)  # Use rule-based response
    return jsonify(response=bot_response)


@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html', user_events=user_events)
    else:
        return redirect(url_for('login'))

@app.route('/add_event', methods=['POST'])
def add_event():
    if 'user_id' in session:
        data = request.json
        name = data.get('event_name')
        date = data.get('date')
        occupancy = data.get('occupancy')

        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO events (name, date, occupancy, creator_id) 
                          VALUES (?, ?, ?, ?)''', (name, date, occupancy, session['user_id']))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Event created successfully!'})
    else:
        return jsonify({'success': False, 'message': 'User not logged in.'})

@app.route('/register_event', methods=['POST'])
def register_event():
    if 'user_id' in session:
        data = request.json
        event_id = data.get('event_id')

        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()

        # Check if the user has already registered
        cursor.execute("SELECT * FROM participation WHERE user_id = ? AND event_id = ?", (session['user_id'], event_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Already registered for this event.'})

        # Register for the event
        cursor.execute("INSERT INTO participation (user_id, event_id) VALUES (?, ?)", (session['user_id'], event_id))

        # Update tickets sold count in events table
        cursor.execute("UPDATE events SET tickets_sold = tickets_sold + 1 WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Registered for event successfully!'})
    else:
        return jsonify({'success': False, 'message': 'User not logged in.'})


def rule_based_response(user_message):
    if "organize" in user_message.lower():
        return "Please provide the event details and your budget."
    elif "budget" in user_message.lower():
        return "The estimated budget for your event is $500. Do you want to proceed?"
    elif "proceed" in user_message.lower():
        send_confirmation_email(session['username'], "Event Organizing Confirmation")
        return "Your event has been organized. A confirmation email has been sent."
    elif "participate" in user_message.lower():
        send_confirmation_email(session['username'], "Event Participation Confirmation")
        return "You have successfully registered for the event. A confirmation email has been sent."
    else:
        return "Welcome! Would you like to organize an event or participate in one?"

def send_confirmation_email(username, subject):
    msg = Message(subject, sender='your_email@example.com', recipients=[f"{username}@example.com"])
    msg.body = f"Hello {username},\n\nYour request for '{subject}' has been confirmed."
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)