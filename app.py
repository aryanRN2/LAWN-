import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'maurya_lawn_secret_key'

# Database Configuration
if os.environ.get('VERCEL'):
    # On Vercel, use the writable /tmp directory
    db_path = '/tmp/bookings_v3.db'
    print(f"VERCEL DETECTED: Using database at {db_path}")
else:
    # On local, use the project directory
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'bookings_v3.db')
    print(f"LOCAL DEV: Using database at {db_path}")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"check_same_thread": False},
    "pool_pre_ping": True
}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    dates = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='pending')  # New field: pending, approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure database is initialized before requests
@app.before_request
def create_tables():
    if os.environ.get('VERCEL'):
        if not os.path.exists('/tmp/bookings_v3.db'):
            try:
                db.create_all()
                # Create default admin
                if not User.query.filter_by(username='chandra221112').first():
                    admin = User(username='chandra221112', password='pxs9rbf4au')
                    db.session.add(admin)
                    db.session.commit()
            except Exception as e:
                print(f"Error creating DB: {e}")
    else:
        # For local dev, create once on startup
        pass

# Local initialization
with app.app_context():
    if not os.environ.get('VERCEL'):
        db.create_all()
        if not User.query.filter_by(username='chandra221112').first():
            new_admin = User(username='chandra221112', password='pxs9rbf4au')
            db.session.add(new_admin)
            db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/booking')
def booking_calendar():
    return render_template('booking.html')

@app.route('/details', methods=['GET', 'POST'])
def booking_details():
    if request.method == 'POST':
        selected_dates = request.form.get('selected_dates')
        if not selected_dates:
            return redirect(url_for('booking_calendar'))
        session['selected_dates'] = selected_dates
        return render_template('details.html', dates=selected_dates)
    
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
        flash("Please fill in all required fields.")
        return redirect(url_for('booking_details'))

    new_booking = Booking(
        name=name,
        phone=phone,
        event_type=event_type,
        description=description,
        dates=dates,
        status='pending'
    )
    db.session.add(new_booking)
    db.session.commit()
    session.pop('selected_dates', None)
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

# Admin Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    all_bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    
    # Approved dates for the calendar
    approved_dates_map = {} # date -> booking info
    approved_dates_list = []
    
    for b in all_bookings:
        if b.dates:
            dates_list = [d.strip() for d in b.dates.split(',')]
            if b.status == 'approved':
                approved_dates_list.extend(dates_list)
                for d in dates_list:
                    approved_dates_map[d] = {
                        'name': b.name,
                        'event': b.event_type,
                        'phone': b.phone
                    }
    
    return render_template('admin.html', 
                           bookings=all_bookings, 
                           approved_dates=approved_dates_list,
                           booked_info=approved_dates_map)

@app.route('/admin/approve/<int:id>')
@login_required
def approve_booking(id):
    booking = Booking.query.get_or_404(id)
    booking.status = 'approved'
    db.session.commit()
    flash(f'Booking for {booking.name} has been approved!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:id>')
@login_required
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted successfully')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
