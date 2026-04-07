# HealthStack System - Setup Instructions

## Problem Identified
- ✅ `.env` file created with SECRET_KEY
- ✅ `settings.py` updated with proper type casting
- ❌ Dependencies not installed in virtual environment
- ❌ Python not in system PATH (but venv exists)

## Solution: Install Dependencies

You have a virtual environment (`venv`) but it doesn't have the required packages installed. Follow these steps:

### Step 1: Open PowerShell or CMD
Navigate to the project directory:
```powershell
cd "c:\Users\salom\OneDrive\Desktop\tm chat\HealthStack-System"
```

### Step 2: Activate Virtual Environment

**For PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**For CMD:**
```cmd
venv\Scripts\activate.bat
```

If you get an execution policy error in PowerShell, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

Once the virtual environment is activated (you'll see `(venv)` in your prompt), run:

```powershell
python -m pip install -r requirements.txt
```

This will install:
- Django 4.1.13
- django-widget-tweaks
- django-rest-framework
- Pillow
- And all other required packages

### Step 4: Install Additional Package

```powershell
python -m pip install --upgrade djangorestframework-simplejwt
```

### Step 5: Run Migrations

```powershell
python manage.py migrate
```

### Step 6: Start the Server

```powershell
python manage.py runserver
```

Then open your browser and go to: `http://127.0.0.1:8000/`

---

## Quick Setup Script

Alternatively, you can run the setup script I created:

**PowerShell:**
```powershell
.\setup.ps1
```

**CMD:**
```cmd
setup.bat
```

---

## Troubleshooting

### If Python is not found:
Make sure you're using the virtual environment's Python:
```powershell
.\venv\Scripts\python.exe --version
```

### If pip install fails:
Try installing packages one by one:
```powershell
python -m pip install Django==4.1.13
python -m pip install django-widget-tweaks==1.4.12
python -m pip install djangorestframework==3.15.2
```

### If you get permission errors:
Run PowerShell or CMD as Administrator, then try again.

---

## Current Status

✅ `.env` file configured
✅ `settings.py` updated with defaults
✅ Virtual environment exists
⏳ **Need to install dependencies** (run Step 3 above)
