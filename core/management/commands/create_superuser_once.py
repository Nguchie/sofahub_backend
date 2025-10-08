from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Create superuser only if none exists'

    def handle(self, *args, **options):
        """Create superuser only if no superusers exist"""
        
        # Check if any superusers already exist
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.SUCCESS('✅ Superuser already exists - skipping creation')
            )
            return
        
        # Get superuser credentials from environment variables
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        
        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR('❌ Missing superuser environment variables')
            )
            self.stdout.write('Required: DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD')
            return
        
        # Create superuser
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Superuser "{username}" created successfully!')
            )
            self.stdout.write('🌐 You can now access the admin panel')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating superuser: {e}')
            )
