@echo off
echo ========================================
echo HealthStack System Setup Script
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 4: Installing requirements...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo Step 5: Installing additional package...
python -m pip install --upgrade djangorestframework-simplejwt

echo.
echo Step 6: Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the server, run:
echo   venv\Scripts\activate.bat
echo   python manage.py runserver
echo.
pause
