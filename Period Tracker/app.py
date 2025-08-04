from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from google_sheets_config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///period_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Google Sheets setup
def setup_google_sheets():
    """Setup Google Sheets connection"""
    try:
        if os.path.exists(CREDENTIALS_FILE):
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
            client = gspread.authorize(creds)
            return client
        return None
    except Exception as e:
        print(f"Google Sheets setup error: {e}")
        return None

def log_to_google_sheets(action, user_id, email, name, ip_address):
    """Log user activity to Google Sheets"""
    try:
        client = setup_google_sheets()
        if client:
            sheet = client.open_by_key(SHEET_ID).worksheet(LOGIN_SHEET_NAME)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row = [timestamp, action, user_id, email, name, ip_address]
            sheet.append_row(row)
    except Exception as e:
        print(f"Google Sheets logging error: {e}")

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)
    pcos = db.Column(db.Boolean, default=False)
    thyroid = db.Column(db.Boolean, default=False)
    anemia = db.Column(db.Boolean, default=False)
    diabetes = db.Column(db.Boolean, default=False)
    emergency_contact = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cycle_settings = db.relationship('CycleSettings', backref='user', uselist=False)
    period_logs = db.relationship('PeriodLog', backref='user', lazy=True)
    mood_trackers = db.relationship('MoodTracker', backref='user', lazy=True)
    favorite_tips = db.relationship('FavoriteTip', backref='user', lazy=True)
    current_period = db.relationship('CurrentPeriod', backref='user', uselist=False)
    water_trackers = db.relationship('WaterTracker', backref='user', lazy=True)
    nutrition_trackers = db.relationship('NutritionTracker', backref='user', lazy=True)

class CycleSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    avg_cycle_length = db.Column(db.Integer, default=28)
    avg_period_length = db.Column(db.Integer, default=5)
    start_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PeriodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expected_date = db.Column(db.Date, nullable=False)
    actual_start_date = db.Column(db.Date)
    delay_days = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MoodTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    mood = db.Column(db.String(50))
    symptoms = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FavoriteTip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tip_text = db.Column(db.Text, nullable=False)
    tip_category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CurrentPeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    expected_end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WaterTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    drank_water = db.Column(db.Boolean, default=False)
    water_amount = db.Column(db.Float, default=0.0)  # in liters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NutritionTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    ate_iron_rich = db.Column(db.Boolean, default=False)
    ate_healthy = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SelfCareActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    activity_type = db.Column(db.String(50))  # exercise, meditation, journaling, etc.
    duration = db.Column(db.Integer)  # in minutes
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EducationalBlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # myths, stories, awareness
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Helper functions
def calculate_next_period(cycle_settings):
    """Calculate next expected period date"""
    if not cycle_settings:
        return None
    
    # Find the last period log
    last_period = PeriodLog.query.filter_by(
        user_id=cycle_settings.user_id
    ).order_by(PeriodLog.expected_date.desc()).first()
    
    if last_period and last_period.actual_start_date:
        # Calculate from last actual period
        next_date = last_period.actual_start_date + timedelta(days=cycle_settings.avg_cycle_length)
    else:
        # Calculate from cycle start date
        next_date = cycle_settings.start_date + timedelta(days=cycle_settings.avg_cycle_length)
    
    return next_date

def calculate_ovulation_window(cycle_settings):
    """Calculate ovulation window (14 days before expected period)"""
    next_period = calculate_next_period(cycle_settings)
    if not next_period:
        return None, None
    
    ovulation_date = next_period - timedelta(days=14)
    ovulation_start = ovulation_date - timedelta(days=2)
    ovulation_end = ovulation_date + timedelta(days=2)
    
    return ovulation_start, ovulation_end

def get_cycle_status(cycle_settings):
    """Get today's cycle status"""
    if not cycle_settings:
        return "No cycle data"
    
    next_period = calculate_next_period(cycle_settings)
    if not next_period:
        return "No cycle data"
    
    today = datetime.now().date()
    days_until = (next_period - today).days
    
    if days_until < 0:
        return "Delayed"
    elif days_until <= 3:
        return "Upcoming"
    else:
        return "On track"

def get_health_tip():
    """Get a random health tip"""
    tips = [
        "🌸 Stay hydrated! Drinking water can help reduce bloating during your period.",
        "💪 Gentle exercise like yoga can help with cramps and mood swings.",
        "😌 Practice self-care with a warm bath or heating pad for comfort.",
        "🫶 Remember, it's okay to take it easy and listen to your body.",
        "🌿 Herbal teas like chamomile can help soothe period symptoms.",
        "💤 Getting enough sleep is crucial for hormonal balance.",
        "🥗 Eating iron-rich foods can help with energy levels during your period.",
        "🧘‍♀️ Deep breathing exercises can help manage stress and anxiety."
    ]
    import random
    return random.choice(tips)

def get_motivational_quote(mood=None):
    """Get a random motivational quote, optionally based on mood"""
    quotes = {
        'happy': [
            "Your joy is contagious! Keep shining! ✨",
            "You're radiating positive energy today! 🌟",
            "Your happiness makes the world brighter! 🌸"
        ],
        'sad': [
            "It's okay to not be okay. Tomorrow is a new day 💕",
            "You're stronger than you know. This too shall pass 🌅",
            "Sending you virtual hugs and warm thoughts 🤗"
        ],
        'tired': [
            "Rest is not a sign of weakness, it's self-care 💤",
            "Take it easy today, you deserve it 😌",
            "Your body is asking for rest - listen to it 🫶"
        ],
        'irritated': [
            "Breathe deeply. You've got this under control 🧘‍♀️",
            "It's okay to feel frustrated. Take a moment for yourself 💆‍♀️",
            "Remember, this feeling is temporary. You're doing great! 💪"
        ],
        'default': [
            "You are stronger than you think! 💪",
            "Every cycle is a fresh start 🌸",
            "Your body is amazing and doing exactly what it should 🫶",
            "You've got this! Take care of yourself today 😌",
            "Remember to be kind to yourself - you're doing great! ✨",
            "Your strength inspires others 💖",
            "Today is a new day full of possibilities 🌅",
            "You are capable of amazing things! 🌟"
        ]
    }
    
    import random
    if mood and mood in quotes:
        return random.choice(quotes[mood])
    return random.choice(quotes['default'])

def get_health_tips_by_mood(mood):
    """Get health tips based on mood"""
    tips = {
        'sad': [
            "🌸 Try gentle yoga or meditation to lift your spirits",
            "💕 Call a friend or family member for support",
            "🎵 Listen to your favorite uplifting music",
            "🌿 Take a walk in nature to clear your mind",
            "🫖 Sip on chamomile tea for natural calming effects"
        ],
        'tired': [
            "💤 Prioritize sleep - aim for 7-9 hours tonight",
            "🥗 Eat iron-rich foods like spinach and lentils",
            "🚶‍♀️ Take short walks to boost energy naturally",
            "💧 Stay hydrated - dehydration can cause fatigue",
            "🧘‍♀️ Try gentle stretching to improve circulation"
        ],
        'irritated': [
            "🧘‍♀️ Practice deep breathing exercises",
            "🌿 Use lavender essential oil for calming effects",
            "📱 Take a break from social media",
            "🎨 Try a creative activity to channel emotions",
            "🏃‍♀️ Light exercise can help release tension"
        ],
        'happy': [
            "🌟 Channel this positive energy into self-care",
            "💪 This is a great time for light exercise",
            "🥗 Maintain healthy eating habits",
            "💧 Keep up with hydration",
            "😌 Practice gratitude journaling"
        ]
    }
    return tips.get(mood, tips['happy'])

def get_health_tips_by_symptoms(symptoms):
    """Get health tips based on symptoms"""
    tips = {
        'cramps': [
            "🔥 Use a heating pad or warm compress",
            "🧘‍♀️ Try gentle yoga poses like child's pose",
            "💊 Consider over-the-counter pain relief",
            "🌿 Drink ginger tea for natural relief",
            "💆‍♀️ Gentle abdominal massage can help"
        ],
        'bloating': [
            "💧 Stay hydrated but avoid carbonated drinks",
            "🥗 Eat smaller, more frequent meals",
            "🧂 Reduce salt intake temporarily",
            "🌿 Try peppermint tea for relief",
            "🚶‍♀️ Light walking can help with digestion"
        ],
        'fatigue': [
            "💤 Listen to your body and rest when needed",
            "🥗 Eat iron-rich foods like spinach",
            "💧 Stay well hydrated",
            "🌅 Get some natural sunlight",
            "🧘‍♀️ Try gentle stretching exercises"
        ],
        'mood_swings': [
            "🧘‍♀️ Practice mindfulness and meditation",
            "📝 Journal your feelings",
            "🌿 Try calming herbal teas",
            "💆‍♀️ Take warm baths with Epsom salts",
            "🎵 Listen to calming music"
        ]
    }
    return tips.get(symptoms, tips['cramps'])

def get_lifestyle_disease_tips(condition):
    """Get tips for lifestyle diseases"""
    tips = {
        'pcos': [
            "🥗 Focus on low-glycemic index foods",
            "💪 Regular exercise helps with insulin resistance",
            "🌿 Consider inositol supplements (consult doctor)",
            "💤 Prioritize sleep for hormonal balance",
            "🧘‍♀️ Stress management is crucial",
            "🥑 Include healthy fats like avocado",
            "🚫 Avoid processed foods and added sugars"
        ],
        'pcod': [
            "🥗 Eat a balanced diet with whole foods",
            "💪 Regular physical activity is important",
            "🌿 Consider natural supplements like cinnamon",
            "💤 Maintain regular sleep schedule",
            "🧘‍♀️ Practice stress-reduction techniques",
            "🥑 Include omega-3 rich foods",
            "🚫 Limit refined carbohydrates"
        ],
        'thyroid': [
            "🥗 Ensure adequate iodine intake",
            "💪 Regular exercise supports thyroid function",
            "🌿 Consider selenium-rich foods like Brazil nuts",
            "💤 Prioritize quality sleep",
            "🧘‍♀️ Manage stress levels",
            "🥑 Include healthy fats for hormone production",
            "🚫 Avoid excessive soy and cruciferous vegetables"
        ]
    }
    return tips.get(condition, tips['pcos'])

def get_cycle_progress_info(cycle_settings):
    """Get detailed cycle progress information including period status"""
    if not cycle_settings:
        return None
    
    today = datetime.now().date()
    next_period = calculate_next_period(cycle_settings)
    
    if not next_period:
        return None
    
    # Check if user is currently in an active period
    current_period = CurrentPeriod.query.filter_by(
        user_id=cycle_settings.user_id,
        is_active=True
    ).first()
    
    if current_period and current_period.start_date <= today <= current_period.expected_end_date:
        days_since_period_start = (today - current_period.start_date).days + 1
        return {
            'status': 'period',
            'day': days_since_period_start,
            'total_days': cycle_settings.avg_period_length,
            'message': f"Day {days_since_period_start} of Period",
            'show_question': False
        }
    
    # Auto-reset: If period has ended, deactivate current period
    if current_period and today > current_period.expected_end_date:
        current_period.is_active = False
        db.session.commit()
    
    # Calculate cycle day from last period start
    last_period = PeriodLog.query.filter_by(
        user_id=cycle_settings.user_id
    ).order_by(PeriodLog.actual_start_date.desc()).first()
    
    if last_period and last_period.actual_start_date:
        cycle_start = last_period.actual_start_date
    else:
        cycle_start = cycle_settings.start_date
    
    cycle_day = (today - cycle_start).days + 1
    
    # Check if we should show the question box
    days_until_period = (next_period - today).days
    show_question = days_until_period <= 0
    
    if show_question:
        delay_days = abs(days_until_period)
        if delay_days == 0:
            message = f"Day {cycle_day} of Cycle"
        else:
            message = f"{delay_days} Day{'s' if delay_days > 1 else ''} Delayed"
    else:
        message = f"Day {cycle_day} of Cycle"
    
    return {
        'status': 'cycle',
        'day': cycle_day,
        'total_days': cycle_settings.avg_cycle_length,
        'message': message,
        'show_question': show_question,
        'delay_days': max(0, -days_until_period)
    }

def get_supportive_message(delay_days):
    """Get supportive messages for delayed periods"""
    messages = [
        "It's okay, sometimes periods can be delayed due to stress, diet, or lifestyle changes.",
        "Don't worry! Period delays are completely normal and can happen for various reasons.",
        "Your body is unique and may not always follow a perfect schedule. That's normal!",
        "Stress, travel, or changes in routine can affect your cycle. Be patient with yourself.",
        "Remember, every woman's cycle is different. Your body knows what it's doing!",
        "Take this time to practice self-care and listen to what your body needs.",
        "Delays can be caused by hormonal fluctuations, which are completely natural.",
        "Your period will come when your body is ready. Trust the process! 💕"
    ]
    
    if delay_days <= 3:
        return messages[0]
    elif delay_days <= 7:
        return messages[1]
    else:
        return messages[2]

def get_lifestyle_disease_advice(user):
    """Get personalized advice based on user's health conditions"""
    advice = {}
    
    if user.pcos:
        advice['pcos'] = {
            'diet': [
                "Include low-glycemic index foods like quinoa, sweet potatoes",
                "Add omega-3 rich foods like salmon, walnuts, flaxseeds",
                "Avoid refined carbs and sugary foods",
                "Include protein with every meal"
            ],
            'exercise': [
                "30 minutes of moderate exercise daily",
                "Strength training 2-3 times per week",
                "Yoga for stress management",
                "Walking or swimming for cardio"
            ],
            'self_care': [
                "Practice stress management techniques",
                "Get 7-8 hours of quality sleep",
                "Monitor blood sugar levels",
                "Regular check-ups with your doctor"
            ]
        }
    
    if user.thyroid:
        advice['thyroid'] = {
            'diet': [
                "Include iodine-rich foods like seaweed, fish",
                "Add selenium-rich foods like Brazil nuts",
                "Avoid goitrogenic foods in excess",
                "Include zinc-rich foods like pumpkin seeds"
            ],
            'exercise': [
                "Gentle exercises like walking, yoga",
                "Avoid over-exertion",
                "Regular but moderate activity",
                "Listen to your body's energy levels"
            ],
            'self_care': [
                "Take medications as prescribed",
                "Regular thyroid function tests",
                "Manage stress levels",
                "Adequate rest and sleep"
            ]
        }
    
    if user.anemia:
        advice['anemia'] = {
            'diet': [
                "Iron-rich foods: spinach, lentils, red meat",
                "Vitamin C with iron for better absorption",
                "Avoid tea/coffee with meals",
                "Include B12 rich foods like eggs, dairy"
            ],
            'exercise': [
                "Start with gentle exercises",
                "Gradually increase intensity",
                "Listen to your body",
                "Rest when needed"
            ],
            'self_care': [
                "Regular iron supplements if prescribed",
                "Monitor energy levels",
                "Adequate sleep and rest",
                "Regular blood tests"
            ]
        }
    
    if user.diabetes:
        advice['diabetes'] = {
            'diet': [
                "Monitor carbohydrate intake",
                "Include fiber-rich foods",
                "Regular meal timing",
                "Portion control"
            ],
            'exercise': [
                "Regular physical activity",
                "Blood sugar monitoring",
                "Consult doctor before new exercises",
                "Stay hydrated during exercise"
            ],
            'self_care': [
                "Regular blood sugar monitoring",
                "Foot care and inspection",
                "Regular medical check-ups",
                "Stress management"
            ]
        }
    
    return advice

def get_water_tracking_stats(user_id):
    """Get water tracking statistics for the current week"""
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    water_entries = WaterTracker.query.filter(
        WaterTracker.user_id == user_id,
        WaterTracker.date >= week_start,
        WaterTracker.date <= week_end
    ).all()
    
    total_days = 7
    days_with_water = len([entry for entry in water_entries if entry.drank_water])
    total_water = sum([entry.water_amount for entry in water_entries])
    
    return {
        'total_days': total_days,
        'days_with_water': days_with_water,
        'total_water': total_water,
        'target_water': total_days * 2.0,  # 2L per day
        'percentage': (days_with_water / total_days) * 100 if total_days > 0 else 0
    }

def get_nutrition_tracking_stats(user_id):
    """Get nutrition tracking statistics for the current week"""
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    nutrition_entries = NutritionTracker.query.filter(
        NutritionTracker.user_id == user_id,
        NutritionTracker.date >= week_start,
        NutritionTracker.date <= week_end
    ).all()
    
    total_days = 7
    days_with_iron = len([entry for entry in nutrition_entries if entry.ate_iron_rich])
    days_healthy = len([entry for entry in nutrition_entries if entry.ate_healthy])
    
    return {
        'total_days': total_days,
        'days_with_iron': days_with_iron,
        'days_healthy': days_healthy,
        'iron_percentage': (days_with_iron / total_days) * 100 if total_days > 0 else 0,
        'healthy_percentage': (days_healthy / total_days) * 100 if total_days > 0 else 0
    }

def get_self_care_activities(user_id, days=7):
    """Get self-care activities for the last N days"""
    today = datetime.now().date()
    start_date = today - timedelta(days=days)
    
    activities = SelfCareActivity.query.filter(
        SelfCareActivity.user_id == user_id,
        SelfCareActivity.date >= start_date
    ).order_by(SelfCareActivity.date.desc()).all()
    
    return activities

# Make helper functions available to templates
@app.context_processor
def utility_processor():
    return {
        'get_health_tips_by_mood': get_health_tips_by_mood,
        'get_health_tips_by_symptoms': get_health_tips_by_symptoms,
        'get_lifestyle_disease_tips': get_lifestyle_disease_tips
    }

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = int(request.form.get('age', 0)) if request.form.get('age') else None
        
        # Health conditions
        pcos = 'pcos' in request.form
        thyroid = 'thyroid' in request.form
        anemia = 'anemia' in request.form
        diabetes = 'diabetes' in request.form
        emergency_contact = request.form.get('emergency_contact', '')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            age=age,
            pcos=pcos,
            thyroid=thyroid,
            anemia=anemia,
            diabetes=diabetes,
            emergency_contact=emergency_contact
        )
        db.session.add(user)
        db.session.commit()
        
        # Log to Google Sheets
        log_to_google_sheets('SIGNUP', user.id, email, name, request.remote_addr)
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            # Log to Google Sheets
            log_to_google_sheets('LOGIN', user.id, email, user.name, request.remote_addr)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Log to Google Sheets before logout
    log_to_google_sheets('LOGOUT', current_user.id, current_user.email, current_user.name, request.remote_addr)
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    cycle_settings = CycleSettings.query.filter_by(user_id=current_user.id).first()
    next_period = calculate_next_period(cycle_settings) if cycle_settings else None
    ovulation_start, ovulation_end = calculate_ovulation_window(cycle_settings) if cycle_settings else (None, None)
    cycle_status = get_cycle_status(cycle_settings)
    health_tip = get_health_tip()
    
    # Get cycle progress information
    cycle_progress = get_cycle_progress_info(cycle_settings)
    
    # Get today's mood entry
    today = datetime.now().date()
    today_mood = MoodTracker.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).first()
    
    # Get water and nutrition tracking stats
    water_stats = get_water_tracking_stats(current_user.id)
    nutrition_stats = get_nutrition_tracking_stats(current_user.id)
    
    # Get lifestyle advice
    lifestyle_advice = get_lifestyle_disease_advice(current_user)
    
    # Get mood-based quote
    quote = get_motivational_quote(today_mood.mood if today_mood else None)
    
    return render_template('dashboard.html',
                         cycle_settings=cycle_settings,
                         next_period=next_period,
                         ovulation_start=ovulation_start,
                         ovulation_end=ovulation_end,
                         cycle_status=cycle_status,
                         cycle_progress=cycle_progress,
                         health_tip=health_tip,
                         today_mood=today_mood,
                         today=today,
                         quote=quote,
                         water_stats=water_stats,
                         nutrition_stats=nutrition_stats,
                         lifestyle_advice=lifestyle_advice)

@app.route('/setup_cycle', methods=['GET', 'POST'])
@login_required
def setup_cycle():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        avg_cycle_length = int(request.form['avg_cycle_length'])
        avg_period_length = int(request.form['avg_period_length'])
        
        # Check if cycle settings already exist
        existing_settings = CycleSettings.query.filter_by(user_id=current_user.id).first()
        if existing_settings:
            existing_settings.start_date = start_date
            existing_settings.avg_cycle_length = avg_cycle_length
            existing_settings.avg_period_length = avg_period_length
        else:
            cycle_settings = CycleSettings(
                user_id=current_user.id,
                start_date=start_date,
                avg_cycle_length=avg_cycle_length,
                avg_period_length=avg_period_length
            )
            db.session.add(cycle_settings)
        
        db.session.commit()
        flash('Cycle settings updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    cycle_settings = CycleSettings.query.filter_by(user_id=current_user.id).first()
    return render_template('setup_cycle.html', cycle_settings=cycle_settings)

@app.route('/period_reminder', methods=['GET', 'POST'])
@login_required
def period_reminder():
    cycle_settings = CycleSettings.query.filter_by(user_id=current_user.id).first()
    if not cycle_settings:
        flash('Please set up your cycle first!', 'error')
        return redirect(url_for('setup_cycle'))
    
    next_period = calculate_next_period(cycle_settings)
    today = datetime.now().date()
    
    if request.method == 'POST':
        has_started = request.form.get('has_started') == 'yes'
        
        if has_started:
            # Create period log
            period_log = PeriodLog(
                user_id=current_user.id,
                expected_date=next_period,
                actual_start_date=today,
                delay_days=0
            )
            db.session.add(period_log)
            db.session.commit()
            
            flash(f'Period logged! {get_motivational_quote()}', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Calculate delay
            delay_days = (today - next_period).days
            if delay_days > 0:
                flash(f'Noted! You\'re {delay_days} day(s) delayed. Don\'t worry, this is normal! 💕', 'info')
            else:
                flash('Noted! We\'ll ask again tomorrow. Take care! 💕', 'info')
            return redirect(url_for('dashboard'))
    
    # Check if we should show reminder
    if next_period and (next_period - today).days <= 0:
        return render_template('period_reminder.html', next_period=next_period)
    
    return redirect(url_for('dashboard'))

@app.route('/confirm_period', methods=['POST'])
@login_required
def confirm_period():
    """Handle smart period confirmation"""
    cycle_settings = CycleSettings.query.filter_by(user_id=current_user.id).first()
    if not cycle_settings:
        return jsonify({'success': False, 'message': 'Please set up your cycle first!'})
    
    data = request.get_json()
    has_started = data.get('has_started', False)
    today = datetime.now().date()
    
    if has_started:
        # Create period log
        next_period = calculate_next_period(cycle_settings)
        delay_days = 0
        if next_period:
            delay_days = max(0, (today - next_period).days)
        
        period_log = PeriodLog(
            user_id=current_user.id,
            expected_date=next_period if next_period else today,
            actual_start_date=today,
            delay_days=delay_days
        )
        db.session.add(period_log)
        
        # Create or update current period tracking
        expected_end_date = today + timedelta(days=cycle_settings.avg_period_length - 1)
        
        # Deactivate any existing current period
        existing_current = CurrentPeriod.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).first()
        if existing_current:
            existing_current.is_active = False
        
        # Create new current period
        current_period = CurrentPeriod(
            user_id=current_user.id,
            start_date=today,
            expected_end_date=expected_end_date,
            is_active=True
        )
        db.session.add(current_period)
        db.session.commit()
        
        # Log to Google Sheets
        log_to_google_sheets('period_confirmed', current_user.id, current_user.email, current_user.name, request.remote_addr)
        
        return jsonify({
            'success': True, 
            'message': 'Period logged successfully! 💕',
            'status': 'period',
            'day': 1,
            'total_days': cycle_settings.avg_period_length,
            'message_text': 'Day 1 of Period'
        })
    else:
        # Log delay
        next_period = calculate_next_period(cycle_settings)
        delay_days = 0
        if next_period:
            delay_days = max(0, (today - next_period).days)
        
        # Log to Google Sheets
        log_to_google_sheets('period_delayed', current_user.id, current_user.email, current_user.name, request.remote_addr)
        
        supportive_message = get_supportive_message(delay_days)
        
        return jsonify({
            'success': True,
            'message': supportive_message,
            'status': 'cycle',
            'delay_days': delay_days,
            'message_text': f"{delay_days} Day{'s' if delay_days > 1 else ''} Delayed" if delay_days > 0 else "Day of Cycle"
        })

@app.route('/get_cycle_progress')
@login_required
def get_cycle_progress():
    """Get current cycle progress for AJAX updates"""
    cycle_settings = CycleSettings.query.filter_by(user_id=current_user.id).first()
    progress_info = get_cycle_progress_info(cycle_settings)
    
    if not progress_info:
        return jsonify({'success': False, 'message': 'No cycle data available'})
    
    return jsonify({
        'success': True,
        'progress': progress_info
    })

@app.route('/complete_period', methods=['POST'])
@login_required
def complete_period():
    """Complete current period and auto-reset cycle"""
    cycle_settings = CycleSettings.query.filter_by(user_id=current_user.id).first()
    if not cycle_settings:
        return jsonify({'success': False, 'message': 'Please set up your cycle first!'})
    
    data = request.get_json()
    duration = data.get('duration', cycle_settings.avg_period_length)
    notes = data.get('notes', '')
    
    # Get current active period
    current_period = CurrentPeriod.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).first()
    
    if not current_period:
        return jsonify({'success': False, 'message': 'No active period found!'})
    
    # Update the period log with duration and notes
    period_log = PeriodLog.query.filter_by(
        user_id=current_user.id,
        actual_start_date=current_period.start_date
    ).first()
    
    if period_log:
        period_log.duration = duration
        period_log.notes = notes
        db.session.commit()
    
    # Deactivate current period
    current_period.is_active = False
    db.session.commit()
    
    # Log to Google Sheets
    log_to_google_sheets('period_completed', current_user.id, current_user.email, current_user.name, request.remote_addr)
    
    return jsonify({
        'success': True,
        'message': 'Period completed! Cycle reset to Day 1 💕',
        'status': 'cycle',
        'day': 1,
        'total_days': cycle_settings.avg_cycle_length,
        'message_text': 'Day 1 of Cycle'
    })

@app.route('/track_mood', methods=['POST'])
@login_required
def track_mood():
    data = request.get_json()
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    mood = data['mood']
    symptoms = data.get('symptoms', '')
    
    # Check if mood entry already exists for this date
    existing_mood = MoodTracker.query.filter_by(
        user_id=current_user.id, 
        date=date
    ).first()
    
    if existing_mood:
        existing_mood.mood = mood
        existing_mood.symptoms = symptoms
    else:
        mood_entry = MoodTracker(
            user_id=current_user.id,
            date=date,
            mood=mood,
            symptoms=symptoms
        )
        db.session.add(mood_entry)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/history')
@login_required
def history():
    # Get last 6 months of data
    six_months_ago = datetime.now().date() - timedelta(days=180)
    period_logs = PeriodLog.query.filter_by(user_id=current_user.id).filter(
        PeriodLog.expected_date >= six_months_ago
    ).order_by(PeriodLog.expected_date.desc()).all()
    
    mood_trackers = MoodTracker.query.filter_by(user_id=current_user.id).filter(
        MoodTracker.date >= six_months_ago
    ).order_by(MoodTracker.date.desc()).all()
    
    return render_template('history.html', period_logs=period_logs, mood_trackers=mood_trackers)

@app.route('/add_period_log', methods=['POST'])
@login_required
def add_period_log():
    expected_date = datetime.strptime(request.form['expected_date'], '%Y-%m-%d').date()
    actual_start_date = datetime.strptime(request.form['actual_start_date'], '%Y-%m-%d').date() if request.form['actual_start_date'] else None
    duration = int(request.form['duration']) if request.form['duration'] else None
    notes = request.form.get('notes', '')
    
    if actual_start_date:
        delay_days = (actual_start_date - expected_date).days
    else:
        delay_days = 0
    
    period_log = PeriodLog(
        user_id=current_user.id,
        expected_date=expected_date,
        actual_start_date=actual_start_date,
        delay_days=delay_days,
        duration=duration,
        notes=notes
    )
    
    db.session.add(period_log)
    db.session.commit()
    
    flash('Period log added successfully!', 'success')
    return redirect(url_for('history'))

@app.route('/health-tips')
@login_required
def health_tips():
    # Get user's current mood for personalized tips
    today = datetime.now().date()
    today_mood = MoodTracker.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).first()
    
    # Get favorite tips
    favorite_tips = FavoriteTip.query.filter_by(user_id=current_user.id).all()
    
    return render_template('health_tips.html', 
                         today_mood=today_mood,
                         favorite_tips=favorite_tips)

@app.route('/period-kit')
@login_required
def period_kit():
    return render_template('period_kit.html')

@app.route('/save_favorite_tip', methods=['POST'])
@login_required
def save_favorite_tip():
    data = request.get_json()
    tip_text = data['tip_text']
    tip_category = data.get('tip_category', 'general')
    
    # Check if tip already exists
    existing_tip = FavoriteTip.query.filter_by(
        user_id=current_user.id,
        tip_text=tip_text
    ).first()
    
    if not existing_tip:
        favorite_tip = FavoriteTip(
            user_id=current_user.id,
            tip_text=tip_text,
            tip_category=tip_category
        )
        db.session.add(favorite_tip)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tip saved to favorites!'})
    
    return jsonify({'success': False, 'message': 'Tip already in favorites!'})

@app.route('/remove_favorite_tip', methods=['POST'])
@login_required
def remove_favorite_tip():
    data = request.get_json()
    tip_id = data['tip_id']
    
    tip = FavoriteTip.query.filter_by(
        id=tip_id,
        user_id=current_user.id
    ).first()
    
    if tip:
        db.session.delete(tip)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tip removed from favorites!'})
    
    return jsonify({'success': False, 'message': 'Tip not found!'})

@app.route('/edit_period_log', methods=['POST'])
@login_required
def edit_period_log():
    log_id = request.form['log_id']
    actual_start_date = datetime.strptime(request.form['actual_start_date'], '%Y-%m-%d').date() if request.form['actual_start_date'] else None
    duration = int(request.form['duration']) if request.form['duration'] else None
    notes = request.form.get('notes', '')
    
    period_log = PeriodLog.query.filter_by(
        id=log_id,
        user_id=current_user.id
    ).first()
    
    if period_log:
        if actual_start_date:
            period_log.actual_start_date = actual_start_date
            period_log.delay_days = (actual_start_date - period_log.expected_date).days
        period_log.duration = duration
        period_log.notes = notes
        db.session.commit()
        flash('Period log updated successfully!', 'success')
    else:
        flash('Period log not found!', 'error')
    
    return redirect(url_for('history'))

@app.route('/track_water', methods=['POST'])
@login_required
def track_water():
    """Track water intake for the day"""
    data = request.get_json()
    drank_water = data.get('drank_water', False)
    water_amount = data.get('water_amount', 2.0)  # Default 2L
    date = datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
    
    # Check if entry exists for today
    existing_entry = WaterTracker.query.filter_by(
        user_id=current_user.id,
        date=date
    ).first()
    
    if existing_entry:
        existing_entry.drank_water = drank_water
        existing_entry.water_amount = water_amount
    else:
        water_entry = WaterTracker(
            user_id=current_user.id,
            date=date,
            drank_water=drank_water,
            water_amount=water_amount
        )
        db.session.add(water_entry)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Water intake logged successfully! 💧'
    })

@app.route('/track_nutrition', methods=['POST'])
@login_required
def track_nutrition():
    """Track nutrition for the day"""
    data = request.get_json()
    ate_iron_rich = data.get('ate_iron_rich', False)
    ate_healthy = data.get('ate_healthy', False)
    notes = data.get('notes', '')
    date = datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
    
    # Check if entry exists for today
    existing_entry = NutritionTracker.query.filter_by(
        user_id=current_user.id,
        date=date
    ).first()
    
    if existing_entry:
        existing_entry.ate_iron_rich = ate_iron_rich
        existing_entry.ate_healthy = ate_healthy
        existing_entry.notes = notes
    else:
        nutrition_entry = NutritionTracker(
            user_id=current_user.id,
            date=date,
            ate_iron_rich=ate_iron_rich,
            ate_healthy=ate_healthy,
            notes=notes
        )
        db.session.add(nutrition_entry)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Nutrition logged successfully! 🥗'
    })

@app.route('/self_care', methods=['GET', 'POST'])
@login_required
def self_care():
    """Self-care activities page"""
    if request.method == 'POST':
        data = request.get_json()
        activity_type = data.get('activity_type')
        duration = data.get('duration', 0)
        notes = data.get('notes', '')
        date = datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        
        activity = SelfCareActivity(
            user_id=current_user.id,
            date=date,
            activity_type=activity_type,
            duration=duration,
            notes=notes
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Self-care activity logged successfully! 🧘‍♀️'
        })
    
    # Get recent activities
    activities = get_self_care_activities(current_user.id, 7)
    
    return render_template('self_care.html', activities=activities)

@app.route('/lifestyle_advice')
@login_required
def lifestyle_advice():
    """Personalized lifestyle advice based on health conditions"""
    advice = get_lifestyle_disease_advice(current_user)
    
    return render_template('lifestyle_advice.html', advice=advice)

@app.route('/educational_blog')
@login_required
def educational_blog():
    """Educational blog about menstrual health"""
    # Get blog posts (you can add sample data or create a blog management system)
    blog_posts = [
        {
            'title': 'Common Period Myths Debunked',
            'content': 'Let\'s talk about some common misconceptions about periods...',
            'category': 'myths',
            'image_url': '/static/images/blog/myths.jpg'
        },
        {
            'title': 'Famous Women Who Broke Period Taboos',
            'content': 'Throughout history, many women have fought against period stigma...',
            'category': 'stories',
            'image_url': '/static/images/blog/stories.jpg'
        },
        {
            'title': 'Understanding Your Menstrual Cycle',
            'content': 'Your menstrual cycle is more than just your period...',
            'category': 'awareness',
            'image_url': '/static/images/blog/awareness.jpg'
        }
    ]
    
    return render_template('educational_blog.html', blog_posts=blog_posts)

@app.route('/blog')
@login_required
def blog():
    return render_template('blog.html')

@app.route('/blog/menstrual-cycle')
@login_required
def menstrual_cycle():
    return render_template('menstrual_cycle.html')

@app.route('/blog/period-taboos')
@login_required
def period_taboos():
    return render_template('period_taboos.html')

@app.route('/blog/period-myths')
@login_required
def period_myths():
    return render_template('period_myths.html')

@app.route('/export_data')
@login_required
def export_data():
    """Export user data to PDF"""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from io import BytesIO
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.pink
    )
    story.append(Paragraph(f"Period Tracker Report for {current_user.name}", title_style))
    story.append(Spacer(1, 20))
    
    # User Info
    story.append(Paragraph("User Information", styles['Heading2']))
    user_info = [
        ['Name', current_user.name],
        ['Email', current_user.email],
        ['Age', str(current_user.age) if current_user.age else 'Not specified'],
        ['Health Conditions', ', '.join([
            'PCOS' if current_user.pcos else '',
            'Thyroid' if current_user.thyroid else '',
            'Anemia' if current_user.anemia else '',
            'Diabetes' if current_user.diabetes else ''
        ]).strip(', ') or 'None']
    ]
    
    user_table = Table(user_info)
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(user_table)
    story.append(Spacer(1, 20))
    
    # Period History
    story.append(Paragraph("Period History (Last 6 Months)", styles['Heading2']))
    period_logs = PeriodLog.query.filter_by(user_id=current_user.id).order_by(PeriodLog.expected_date.desc()).limit(6).all()
    
    if period_logs:
        period_data = [['Expected Date', 'Actual Date', 'Delay', 'Duration', 'Notes']]
        for log in period_logs:
            period_data.append([
                log.expected_date.strftime('%Y-%m-%d'),
                log.actual_start_date.strftime('%Y-%m-%d') if log.actual_start_date else 'Not logged',
                str(log.delay_days) if log.delay_days else '0',
                str(log.duration) if log.duration else 'Not specified',
                log.notes or 'No notes'
            ])
        
        period_table = Table(period_data)
        period_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(period_table)
    else:
        story.append(Paragraph("No period data available", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    from flask import send_file
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'period_tracker_report_{current_user.name}_{datetime.now().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 