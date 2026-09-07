# VAHAD – Tourist Management System (VAHAD-TMS)

[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12%20|%203.13-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20|%20MySQL%20|%20SQLite-orange.svg)]()
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

**VAHAD-TMS** is a modern, enterprise-grade, responsive, and secure Django tourist management web application. It features destination discovery, multi-tier categorized itineraries, gamified rewards, booking lifecycle management, demo payment simulation, and user profiles.

---

## Key Features

- **Destination Catalog & Discovery**: Rich search by keywords, location filters, and category navigation.
- **Smart Booking System**: Server-side validated booking workflow with travel date guards and traveler limits.
- **Accurate Financial Calculations**: Strict `Decimal` arithmetic for accurate pricing across Budget (0.8x), Standard (1.0x), and Luxury (2.5x) tiers.
- **Secure Demo Payment Gateway**: CSRF-protected payment authorization with optional VIP Protection add-on (+₹2,999).
- **IDOR Protection & Authorization**: Strict user-level access controls ensuring travelers cannot view, modify, or cancel other users' bookings.
- **User Dashboard & Profiles**: View personal bookings, track status, update contact details, and upload profile photos.
- **Loyalty Rewards Program**: Tier-based gamification (*Explorer*, *Voyager*, *Globe Trotter*, *Vahad Legend*) with live coupon code generators.
- **Django Admin Interface**: Customized management panel with search, filters, and batch controls for destinations, categories, bookings, and users.
- **Health Check Endpoint**: Operational `/health/` monitoring probe for load balancers and container orchestrators.
- **Production Ready**: Zero runtime migrations in WSGI, environment-driven secrets, WhiteNoise static compression, and Docker support.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Modern JavaScript, Google Fonts (*Outfit*, *Poppins*) |
| **Backend** | Python 3.12 / 3.13, Django Framework |
| **Database** | PostgreSQL (Production) / MySQL / SQLite (Local Dev) |
| **Static Files** | WhiteNoise (Compressed Static Storage) |
| **WSGI Server** | Gunicorn |
| **Containerization** | Docker, Docker Compose |

---

## Project Structure

```
VAHAD-TMS-main/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── build.sh
├── .env.example
├── .gitignore
├── README.md
├── populate_db.py
│
├── vahad_project/             # Project Configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── mysql_setup.py
│
├── vahad_app/                 # Main Application
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py   # Safe, idempotent data seeding command
│   ├── migrations/
│   └── templates/             # HTML Templates & Custom Error Pages
│       ├── 403.html
│       ├── 404.html
│       ├── 500.html
│       └── vahad_app/
│           ├── base.html
│           ├── home.html
│           ├── destinations.html
│           ├── destination_detail.html
│           ├── booking.html
│           ├── payment.html
│           ├── confirmation.html
│           ├── profile.html
│           ├── rewards.html
│           ├── premium.html
│           ├── about.html
│           ├── register.html
│           └── login.html
│
├── static/                    # Custom CSS, JS, and Assets
│   ├── css/
│   └── js/
│
└── media/                     # User Uploads and Media
    ├── category_images/
    ├── destination_images/
    └── profile_photos/
```

---

## Local Installation & Setup

### 1. Clone or Extract Project
Open a terminal in the project directory:
```bash
cd VAHAD-TMS-main
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` for local development:
```env
DJANGO_SECRET_KEY=local-development-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
USE_SQLITE=True
TIME_ZONE=Asia/Kolkata
```

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Seed Sample Data (Idempotent)
Populates initial categories (Beaches, Hill Stations, Temples, etc.) and featured destinations without creating default admin credentials:
```bash
python manage.py seed_data
```

### 7. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 8. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 9. Run Test Suite
```bash
python manage.py test
```

### 10. Start Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your web browser.

---

## Production Deployment

### 1. Recommended Production Architecture
- **Web Host**: Render, Railway, Fly.io, AWS ECS, or DigitalOcean App Platform.
- **Database**: Managed PostgreSQL (e.g. Supabase, Neon, AWS RDS, Render Postgres).
- **Static Assets**: WhiteNoise (`CompressedStaticFilesStorage`).
- **Media Assets**: Persistent Disk or S3-compatible Object Storage (AWS S3, Cloudflare R2).

### 2. Production Environment Variables
Set the following environment variables in your hosting dashboard:

```env
DJANGO_SECRET_KEY=generate-a-strong-50-character-random-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-service.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://your-service.onrender.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
TIME_ZONE=Asia/Kolkata

# HTTPS / SSL Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### 3. Build & Release Commands
- **Build Phase**:
  ```bash
  pip install -r requirements.txt
  python manage.py collectstatic --noinput
  ```
- **Release Phase**:
  ```bash
  python manage.py migrate --noinput
  python manage.py seed_data
  ```
- **Start Command**:
  ```bash
  gunicorn vahad_project.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --access-logfile - --error-logfile -
  ```

---

## Docker Deployment

### Run with Docker Compose (Web + PostgreSQL)
```bash
docker-compose up --build -d
```

Check health status:
```bash
curl http://localhost:8000/health/
```

Run migrations and seed data in container:
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_data
```

Stop services:
```bash
docker-compose down
```

---

## Security Highlights

1. **Strict IDOR Prevention**: Booking queries, payments, confirmations, and cancellations verify user ownership: `get_object_or_404(Booking, booking_id=booking_id, user=request.user)`.
2. **CSRF-Protected Payment Flow**: Payment status transitions occur strictly through authenticated POST requests.
3. **Pillow Image Verification**: All avatar uploads are inspected with Pillow to prevent malicious file uploads (5MB max limit, JPG/PNG/WEBP whitelist).
4. **Sanitized Health Check**: `/health/` probe reports database status without exposing internal hostnames or credentials.
5. **No WSGI Runtime Migrations**: Database initialization is decoupled from WSGI startup.
6. **Zero Hardcoded Secrets**: Production secrets and database passwords are read exclusively from environment variables.

---

## License & Support
VAHAD Tourist Management System (VAHAD-TMS) © 2026. All rights reserved.
