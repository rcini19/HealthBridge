# 🏥 HealthBridge

## 📖 Project Description
HealthBridge is an online platform designed to connect users with nearby pharmacies and medical resources.  
It allows users to search for medicines, request supplies, and manage health-related transactions efficiently.  
The system provides a user-friendly interface for both customers and administrators to ensure smooth and accessible healthcare support.

**Key Features:**
- 🔍 Medicine search and availability tracking
- 📦 Donation management system
- ⏰ **Automated expiry monitoring** (checks every 2 minutes)
- 📧 Email alerts for expiring medicines
- 👤 User authentication and profiles
- ☁️ Cloud database with Supabase PostgreSQL

---

## 🧰 Tech Stack Used
- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Python (Django Framework)  
- **Database:** Supabase (PostgreSQL)
- **Monitoring:** Automated background service
- **Email:** Brevo API (recommended for production), Resend, or SMTP (Gmail/Outlook/Yahoo)

---

## 🚀 Quick Setup (Recommended)

### Prerequisites
- Python 3.8 or higher
- Git
- Internet connection

### One-Click Setup
```bash
# Step 1: Clone the repository
git clone https://github.com/Caleeeeeeeeeb/HealthBridge.git
cd HealthBridge

# Step 2: Run automated setup
setup.bat
```

### Configure Environment Variables
### go to project set up notepadfile

### Run Migrations & Start
```bash
# Activate virtual environment
env\Scripts\activate

# Run database migrations
python manage.py migrate

# Create admin account (optional)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 🔄 Background Monitor (Automated Expiry Checks)

### Features
- ✅ Monitors Supabase database every 2 minutes
- ✅ Sends email alerts for medicines expiring within 10 days
- ✅ Runs silently in background (no popup windows)
- ✅ Auto-start on Windows login (optional)

### Start Background Monitor
```bash
start_monitor.bat
```

### Stop Background Monitor
```bash
powershell -File stop_monitor.ps1
```

### Enable Auto-Start (Optional)
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_autostart.ps1
```

---

## 📋 Manual Setup (Alternative)

```bash
# Clone repository
git clone https://github.com/Caleeeeeeeeeb/HealthBridge.git
cd HealthBridge

# Create virtual environment
python -m venv env
env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure .env file (see above)

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

---

## 🛠️ Common Commands

| Task | Command |
|------|---------|
| Activate virtual environment | `env\Scripts\activate` |
| Start development server | `python manage.py runserver` |
| Run migrations | `python manage.py migrate` |
| Create superuser | `python manage.py createsuperuser` |
| Check expiry manually | `python manage.py check_expiry` |
| Start background monitor | `start_monitor.bat` |
| Stop background monitor | `.\stop_monitor.ps1` |

---

## 📁 Important Files

- **`setup.bat`** - One-click setup script
- **`start_monitor.bat`** - Start background expiry monitor
- **`stop_monitor.ps1`** - Stop background monitor
- **`realtime_monitor.py`** - Supabase monitoring script
- **`.env`** - Configuration (DO NOT commit to Git!)
- **`SETUP_GUIDE.md`** - Detailed setup instructions
- **`requirements.txt`** - Python dependencies

---

## 🐛 Troubleshooting

**Database Connection Failed:**
- Verify `.env` has correct `DATABASE_URL`
- Check internet connection
- Run: `python manage.py migrate`

**Monitor Not Working:**
- Stop existing monitors: `.\stop_monitor.ps1`
- Start fresh: `start_monitor.bat`
- Check Task Manager for `pythonw.exe`

**Popup Windows Appearing:**
- Use `start_monitor.bat` (not direct Python)
- Updated monitor uses subprocess (no popups)

See **SETUP_GUIDE.md** for detailed troubleshooting.

---

## 👨‍💻 Team Members

| Name | Role | CIT-U Email |
|------|------|-------------|
| Terence Ed N. Limpio | Project Manager | terenceed.limpio@cit.edu |
| Keith Daniel P. Lim | Business Analyst | keithdaniel.lim@cit.edu |
| Rhyz Nhicco C. Libetario | Scrum Master | rhyznhicco.libetario@cit.edu |
| Junjie L. Geraldez | Lead Developer | junjie.geraldez@cit.edu |
| Benz Leo A. Gamallo | Developer | benzleo.gamallo@cit.edu |
| Rudyard Axel L. Gersamio | Developer | rudyardaxle.gersamiol@cit.edu |

---

## 📄 License
This project is part of an academic requirement.

## 🔗 Links
- **Repository:** https://github.com/Caleeeeeeeeeb/HealthBridge
- **Database:** Supabase PostgreSQL (Cloud)
- **Detailed Setup:** See `SETUP_GUIDE.md`

---

**Status:** ✅ Production Ready  
**Version:** 2.0 (Supabase Edition)  
**Last Updated:** October 15, 2025

