# 🏥 HealthBridge

## 📖 Project Description
HealthBridge is an online platform designed to connect users with nearby pharmacies and medical resources.  
It allows users to search for medicines, request supplies, and manage health-related transactions efficiently.  
The system provides a user-friendly interface for both customers and administrators to ensure smooth and accessible healthcare support.

**Key Features:**
- 🔍 Medicine search and availability tracking
- 📦 Donation management system
- ⏰ **Automated expiry monitoring** via GitHub Actions
- 📧 Email alerts for expiring medicines (powered by Brevo)
- 🗑️ Automated cleanup of expired donations
- 👤 User authentication and profiles
- ☁️ Cloud database with Supabase PostgreSQL
- 🔔 In-app notification system

---

## 🧰 Tech Stack Used
- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Python (Django Framework)  
- **Database:** Supabase (PostgreSQL)
- **Storage:** Supabase Storage
- **Automation:** GitHub Actions
- **Email:** Brevo API (HTTPS-based, bypasses port restrictions)

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

## ⚙️ GitHub Actions Automation

### Automated Workflows
HealthBridge uses GitHub Actions for automated tasks:

1. **Daily Expiry Notifications** (8 AM UTC / 4 PM Philippine Time)
   - Checks for medicines expiring within 10 days
   - Sends email alerts to donors via Brevo API

2. **Weekly Cleanup** (Sunday 12 AM UTC / 8 AM Philippine Time)
   - Deletes donations expired for 7+ days
   - Removes images from Supabase Storage
   - Deletes related medicine requests
   - Sends in-app notifications to donors and recipients

### Required GitHub Secrets
Navigate to `Settings` → `Secrets and variables` → `Actions` and add:
- `DATABASE_URL` - Supabase PostgreSQL connection string
- `BREVO_API_KEY` - Brevo email API key
- `BREVO_FROM_EMAIL` - Sender email address
- `BREVO_FROM_NAME` - Sender display name
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service role key
- `SUPABASE_BUCKET_NAME` - Storage bucket name

### Manual Trigger
Go to `Actions` tab → Select workflow → Click `Run workflow`

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
| Check expiry manually | `python manage.py check_expiry --days=10` |
| Cleanup expired (dry-run) | `python manage.py cleanup_expired --dry-run` |
| Cleanup expired (force) | `python manage.py cleanup_expired --days-past-expiry=7` |

---

## 📁 Important Files

- **`setup.bat`** - One-click setup script
- **`.env`** - Configuration (DO NOT commit to Git!)
- **`requirements.txt`** - Python dependencies
- **`.github/workflows/`** - GitHub Actions automation workflows
  - `check_expiry.yml` - Daily expiry notifications
  - `cleanup_expired.yml` - Weekly cleanup automation

---

## 🐛 Troubleshooting

**Database Connection Failed:**
- Verify `.env` has correct `DATABASE_URL`
- Check internet connection
- Run: `python manage.py migrate`

**Emails Not Sending:**
- Verify Brevo API key in `.env`
- Check sender email is verified in Brevo dashboard
- Test manually: `python manage.py check_expiry --days=10`

**GitHub Actions Failing:**
- Verify all 7 secrets are configured in repository settings
- Check workflow logs in Actions tab
- Ensure DATABASE_URL includes `?sslmode=require`

**Images Not Deleting:**
- Verify `SUPABASE_KEY` has storage permissions
- Check `SUPABASE_BUCKET_NAME` matches your bucket

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
- **Repository:** https://github.com/rcini19/HealthBridge
- **Database:** Supabase PostgreSQL (Cloud)
- **Email Service:** Brevo API

---

**Status:** ✅ Production Ready  
**Version:** 3.0 (GitHub Actions + Brevo Edition)  
**Last Updated:** December 5, 2025

