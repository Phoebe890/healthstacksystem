#!/usr/bin/env python
"""
HealthStack System - Setup Verification Script
This script verifies that all dependencies are installed correctly.
"""

import sys
import importlib

def check_module(module_name, package_name=None):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"[OK] {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"[MISSING] {package_name or module_name}: {e}")
        return False

def main():
    print("=" * 60)
    print("HealthStack System - Dependency Verification")
    print("=" * 60)
    print()
    
    required_modules = [
        ('django', 'Django'),
        ('environ', 'django-environ'),
        ('widget_tweaks', 'django-widget-tweaks'),
        ('rest_framework', 'djangorestframework'),
        ('rest_framework_simplejwt', 'djangorestframework-simplejwt'),
        ('PIL', 'Pillow'),
        ('reportlab', 'reportlab'),
        ('xhtml2pdf', 'xhtml2pdf'),
        ('sslcommerz', 'sslcommerz-lib'),
        ('whitenoise', 'whitenoise'),
        ('debug_toolbar', 'django-debug-toolbar'),
    ]
    
    all_ok = True
    for module, package in required_modules:
        if not check_module(module, package):
            all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("[SUCCESS] All dependencies are installed correctly!")
        print()
        print("To start the server, run:")
        print("  .\\venv\\Scripts\\python.exe manage.py runserver")
    else:
        print("[ERROR] Some dependencies are missing!")
        print("Run: .\\venv\\Scripts\\python.exe -m pip install -r requirements.txt")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
