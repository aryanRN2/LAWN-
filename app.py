import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'maurya_lawn_secret_key'

# Database Configuration
# Using /tmp for SQLite to make it somewhat compatible with Vercel's ephemeral filesystem
# though a persistent DB like Vercel Postgres is recommended for production.
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'bookings.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    dates = db.Column(db.String(500), nullable=False)  # Stored as comma-separated strings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.name} - {self.event_type}>'

# Create database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/booking')
def booking_calendar():
    return render_template('booking.html')

@app.route('/details', methods=['GET', 'POST'])
def booking_details():
    if request.method == 'POST':
        # Dates coming from calendar selection
        selected_dates = request.form.get('selected_dates')
        if not selected_dates:
            return redirect(url_for('booking_calendar'))
        session['selected_dates'] = selected_dates
        return render_template('details.html', dates=selected_dates)
    
    # If GET, check if dates in session
    dates = session.get('selected_dates')
    if not dates:
        return redirect(url_for('booking_calendar'))
    return render_template('details.html', dates=dates)

@app.route('/confirm', methods=['POST'])
def confirm_booking():
    name = request.form.get('name')
    phone = request.form.get('phone')
    event_type = request.form.get('event_type')
    description = request.form.get('description')
    dates = session.get('selected_dates')

    if not all([name, phone, event_type, dates]):
        return "Missing details", 400

    new_booking = Booking(
        name=name,
        phone=phone,
        event_type=event_type,
        description=description,
        dates=dates
    )
    db.session.add(new_booking)
    db.session.commit()
    
    # Clear session
    session.pop('selected_dates', None)
    
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)
