
# 🌸 Period Tracker

A modern, aesthetic, and user-friendly Period Tracker Web Application built with Python Flask. This app helps women track their periods, ovulation, delays, and provides health tips dynamically with a beautiful Pinterest-inspired design.

## ✨ Features

### 🔐 User Authentication
- **Sign Up / Login / Logout** system with secure password hashing
- **Session management** for user privacy
- **Private data storage** - each user's data is completely separate

### 📅 Cycle Setup & Tracking
- **Smart cycle prediction** based on user input
- **Period start date** tracking
- **Average cycle length** and **period length** configuration
- **Next period prediction** with intelligent algorithms
- **Ovulation window** calculation (14 days before expected period)

### 🔔 Daily Period Reminders
- **Gentle daily reminders** when period is expected
- **Comforting messages** and support
- **Delay tracking** with encouraging messages
- **Health consultation suggestions** after 7 days delay

### 📊 Comprehensive Dashboard
- **Today's cycle status** (On time, Delayed, Upcoming)
- **Ovulation prediction window**
- **Daily mood tracking** with emoji selection
- **Symptom logging** and notes
- **Health tips of the day** with rotating content
- **Quick action buttons** for easy navigation

### 📝 Cycle History & Analytics
- **Complete period logs** with expected vs actual dates
- **Delay tracking** and visualization
- **Mood and symptoms history**
- **Manual period log addition**
- **Monthly cycle analysis**

### 💅 Beautiful Design
- **Pinterest-inspired aesthetic** with soft colors
- **Mobile-friendly responsive design**
- **Gradient backgrounds** and smooth animations
- **Cute icons** and emojis throughout
- **Bootstrap 5** for modern UI components
- **Custom illustrations** and stickers
- **Hover glow effects** and custom cursors
- **Hero banners** with period-tracking illustrations

### 🧘‍♀️ Health Tips & Wellness
- **Dedicated health tips page** with personalized advice
- **Mood-based tips** (sad, tired, irritated, happy)
- **Symptom-based relief** (cramps, bloating, fatigue, mood swings)
- **Lifestyle disease section** (PCOS, PCOD, Thyroid)
- **Accordion-style layout** for clean organization
- **Save favorite tips** functionality
- **Beautiful health illustrations** and pastel stickers

### 📈 Enhanced Cycle History
- **Last 6 months tracking** with visual data presentation
- **Visual delay markers** (1-day, 2-day, week, extended)
- **Manual correction option** for period logs
- **Monthly auto-updates** and data storage
- **Cute stylized tables** with hover effects

### 🔐 Google Sheets Integration
- **User login data logging** to Google Sheets
- **Secure API integration** with service accounts
- **Comprehensive setup guide** included
- **Privacy-compliant** data handling

## 🛠 Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (easily upgradable to PostgreSQL/MySQL)
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Poppins)
- **Google Sheets**: gspread, Google Sheets API
- **Date/Time**: Python datetime, dateutil

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd period-tracker
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Step 5: Google Sheets Integration (Optional)
For user login data logging to Google Sheets:

1. Follow the detailed setup guide in `GOOGLE_SHEETS_SETUP.md`
2. Configure your credentials in `google_sheets_config.py`
3. The integration will automatically log user signups, logins, and logouts

## 📱 Usage Guide

### 1. Getting Started
- **Register** a new account or **login** with existing credentials
- **Setup your cycle** by providing:
  - Last period start date
  - Average cycle length (21-35 days)
  - Average period length (2-8 days)

### 2. Dashboard Features
- **View cycle status** and next period prediction
- **Track daily mood** using emoji selection
- **Log symptoms** and notes
- **Get health tips** and motivational quotes
- **Access quick actions** for common tasks

### 3. Period Tracking
- **Daily reminders** when period is expected
- **Log actual period start** when it begins
- **Track delays** and get supportive messages
- **View cycle history** and patterns

### 4. Health Monitoring
- **Mood tracking** with 6 different mood options
- **Symptom logging** for comprehensive health monitoring
- **Health tips** tailored for different cycle phases
- **Ovulation window** tracking for fertility awareness

### 5. Health Tips & Wellness
- **Access dedicated health tips page** from navigation
- **Get personalized tips** based on your current mood
- **Browse symptom-based relief** for cramps, bloating, etc.
- **Learn about lifestyle conditions** (PCOS, PCOD, Thyroid)
- **Save favorite tips** for quick access
- **Beautiful accordion layout** for easy navigation

### 6. Enhanced History
- **View last 6 months** of cycle data
- **Visual delay indicators** with color-coded badges
- **Edit period logs** with modal popups
- **Track mood history** with detailed entries
- **Manual data correction** for accuracy

## 🗃 Database Models

### User
- `id`: Primary key
- `name`: User's full name
- `email`: Unique email address
- `password_hash`: Encrypted password
- `created_at`: Account creation timestamp

### CycleSettings
- `user_id`: Foreign key to User
- `avg_cycle_length`: Average days between periods
- `avg_period_length`: Average period duration
- `start_date`: Last period start date

### PeriodLog
- `user_id`: Foreign key to User
- `expected_date`: Predicted period start
- `actual_start_date`: Actual period start
- `delay_days`: Days of delay (positive/negative)
- `duration`: Period duration in days
- `notes`: Optional notes

### MoodTracker
- `user_id`: Foreign key to User
- `date`: Date of mood entry
- `mood`: Selected mood (happy, good, neutral, sad, cramps, tired)
- `symptoms`: Optional symptom notes

### FavoriteTip
- `user_id`: Foreign key to User
- `tip_text`: The health tip content
- `tip_category`: Category of the tip (mood, symptom, lifestyle)
- `created_at`: When the tip was saved

## 🎨 Design Features

### Color Palette
- **Primary Pink**: #ff69b4
- **Light Pink**: #ffb6c1
- **Lavender**: #e6e6fa
- **Soft Purple**: #d8bfd8
- **Pastel Blue**: #b0e0e6
- **Soft Yellow**: #f0e68c

### UI Elements
- **Rounded corners** (20px border-radius)
- **Soft shadows** and hover effects
- **Gradient backgrounds** for visual appeal
- **Responsive design** for all screen sizes
- **Smooth animations** and transitions

## 🔒 Security Features

- **Password hashing** using Werkzeug
- **Session management** with Flask-Login
- **CSRF protection** (built into Flask)
- **Private user data** - no cross-user data access
- **Secure cookie handling**

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. **Change secret key** in `app.py`
2. **Use production database** (PostgreSQL/MySQL)
3. **Set up environment variables**
4. **Use WSGI server** (Gunicorn/uWSGI)
5. **Configure reverse proxy** (Nginx)

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key
export DATABASE_URL=your-database-url
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💖 Support

This application is built with love for women's health and empowerment. If you find it helpful, please consider:

- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing code

## 🏥 Medical Disclaimer

This application is for informational purposes only and should not replace professional medical advice. Always consult with a healthcare provider for medical concerns.

---

**Made with ❤️ for women's health and empowerment** 
=======
# Period_Tracker1
>>>>>>> 257e91e02988abb0b5e16e3ddceff8363400ef85
