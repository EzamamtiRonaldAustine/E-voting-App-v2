# Django Application Setup Documentation

## Overview
This document outlines the complete setup process for the E-Voting Django REST Framework application, including dependencies, installation steps, challenges encountered, and their solutions.

---

## System Requirements

- **Python**: 3.11+ (tested with Python 3.11)
- **Python Package Manager**: pip (25.3+)
- **Operating System**: Windows/Linux/macOS
- **Database**: SQLite (default, included with Django)

---

## Dependencies Installed

### Core Django Packages
```
django>=4.2,<5.1
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
```

### Detailed Package Versions Installed
- **Django 6.0.3**: Web framework for building APIs
- **Django REST Framework 3.17.0**: Toolkit for building REST APIs
- **djangorestframework-simplejwt 5.5.1**: JWT authentication for REST APIs
- **PyJWT 2.12.1**: JSON Web Token implementation
- **asgiref 3.11.1**: ASGI utilities for async support
- **sqlparse 0.5.5**: SQL parsing library
- **tzdata 2025.3**: Timezone database

---

## Installation Steps

### 1. Create Virtual Environment
```bash
cd evoting-app-backend
python -m venv venv
```

**Why?** Virtual environments isolate project dependencies and prevent conflicts with system-wide Python packages.

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
.\venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Database Migrations
```bash
python manage.py makemigrations accounts elections voting audit
```

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. Seed Default Admin User
```bash
python manage.py seed_admin
```

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

### 7. Run Development Server
```bash
python manage.py runserver
```

**Server URL:** `http://localhost:8000`

---

## Challenges & Solutions

### Challenge 1: ModuleNotFoundError - Django Not Found

**Problem:**
```
ModuleNotFoundError: No module named 'django'
ImportError: Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable? Did you forget to activate a virtual environment?
```

**Root Cause:**
Dependencies were installed in the global Python environment (Python 3.11), but the shell was using a different Python version (Python 3.14.3).

**Solution:**
1. Created a dedicated virtual environment for the project using `python -m venv venv`
2. Activated the virtual environment before running any commands
3. Installed all dependencies within the virtual environment using `.\venv\Scripts\pip.exe install -r requirements.txt`
4. Used the venv's Python executable directly: `.\venv\Scripts\python.exe manage.py <command>`

**Key Lesson:** Always activate the virtual environment before working with the project. The venv ensures all packages are isolated and available.

---

### Challenge 2: Incomplete/Corrupted Package Installation

**Problem:**
```
ModuleNotFoundError: No module named 'django.utils'
```

**Root Cause:**
Network timeout during package download caused Django to be partially installed. The package was corrupted with missing submodules.

**Solution:**
1. Performed a fresh installation using the `--no-cache-dir` flag to bypass cached downloads
2. Upgraded pip to the latest version to ensure compatibility
3. Ran: `pip install --upgrade django djangorestframework djangorestframework-simplejwt --no-cache-dir`

**Verification:** After fresh installation, Django 6.0.3 was successfully installed with all required modules.

---

### Challenge 3: Network Connection Issues During Installation

**Problem:**
```
WARNING: Connection timed out while downloading
WARNING: Attempting to resume incomplete download
```

**Root Cause:**
Network instability or slow internet connection during large package downloads (Django 8.2 MB).

**Solution:**
1. Used pip's automatic resume feature which retried the download
2. Ensured stable internet connection before retrying
3. Used `--no-cache-dir` flag to force fresh downloads instead of using cached versions

---

### Challenge 4: PowerShell Path Quoting Issues

**Problem:**
```
Unexpected token 'manage.py' in expression or statement
```

**Root Cause:**
PowerShell interpreted the long path with spaces incorrectly when using double quotes around the full Python path.

**Solution:**
Used single quotes instead of double quotes for paths containing spaces:
```bash
# ❌ Incorrect (double quotes)
"C:\Users\USER\AppData\Local\...\python.exe" manage.py ...

# ✅ Correct (single quotes)
'c:\Users\USER\Desktop\E-vote v2\E-voting-App-v2\evoting-app-backend'
```

---

## Architecture Overview

```
evoting/              → Project settings, root URL config
├── accounts/         → User authentication, JWT, voter/admin management
├── elections/        → Candidates, voting stations, positions, polls
├── voting/           → Vote casting, results, statistics
├── audit/            → Audit trail logging
└── db.sqlite3        → SQLite database file
```

### Layered Architecture Pattern

| Layer       | File             | Responsibility                      |
|-------------|------------------|-------------------------------------|
| Models      | `models.py`      | Data schema and domain properties   |
| Serializers | `serializers.py` | Validation, input/output shaping    |
| Services    | `services.py`    | Business logic and orchestration    |
| Views       | `views.py`       | HTTP handling, delegates to service |
| Permissions | `permissions.py` | Role-based access control (RBAC)    |
| URLs        | `urls.py`        | Route registration                  |

---

## Default Credentials

After running `seed_admin`, the following admin account is created:

| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `admin123` |

**Admin Access:**
- **Django Admin Panel:** `http://localhost:8000/admin/`
- **API Endpoint:** `/api/accounts/login/admin/`

---

## Verification Checklist

After setup, verify the following:

- [ ] Virtual environment activated: `which python` shows venv path
- [ ] All dependencies installed: `pip list` shows Django, DRF, etc.
- [ ] Database migrations applied: `db.sqlite3` file exists
- [ ] Admin user created: Can login to `http://localhost:8000/admin/`
- [ ] Development server running: No errors on `python manage.py runserver`
- [ ] API accessible: Can reach `http://localhost:8000/api/`

---

## Common Commands Reference

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Create migrations
python manage.py makemigrations accounts elections voting audit

# Apply migrations
python manage.py migrate

# Create superuser (interactive)
python manage.py createsuperuser

# Seed default admin
python manage.py seed_admin

# Run development server
python manage.py runserver

# Run tests
python manage.py test

# Access Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

---

## Troubleshooting Guide

### Issue: "No module named 'django'"
**Solution:** Ensure virtual environment is activated: `.\venv\Scripts\Activate.ps1`

### Issue: Database locked error
**Solution:** Delete `db.sqlite3` and run migrations again if database is corrupt.

### Issue: Port 8000 already in use
**Solution:** Run on different port: `python manage.py runserver 8001`

### Issue: Static files not loading
**Solution:** Run `python manage.py collectstatic`

---

## Next Steps

1. **Frontend Setup:** Install and configure the Next.js frontend application
2. **Environment Configuration:** Create `.env` file for production settings
3. **API Testing:** Use Postman or curl to test endpoints
4. **Database Backup:** Set up regular backups of SQLite database
5. **Deployment:** Configure for production using Gunicorn, Nginx, etc.

---

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)

---

**Setup Date:** March 19, 2026  
**Django Version:** 6.0.3  
**Python Version:** 3.11+  
**Status:** ✅ Complete & Tested
