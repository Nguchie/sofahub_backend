#!/usr/bin/env python
"""
Script to set up the deployed database with migrations and admin user.
Run this script after Railway deployment to initialize the database.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_deployment():
    """Set up the database for deployment"""
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sofahub_backend.settings')
    django.setup()
    
    print("🚀 Setting up deployment database...")
    
    # Run migrations
    print("📦 Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Database setup complete!")
    print("🌐 You can now access the admin panel at: https://sofahubbackend-production.up.railway.app/admin/")
    print("👤 Note: You'll need to create an admin user manually through Django shell or admin interface")

if __name__ == '__main__':
    setup_deployment()
