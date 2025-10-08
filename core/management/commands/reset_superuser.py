from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Reset superuser password and ensure correct permissions'

    def handle(self, *args, **options):
        """Reset superuser password and permissions"""
        
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
        
        # Find or create superuser
        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'✅ Created new superuser: {username}')
            else:
                self.stdout.write(f'🔄 Found existing user: {username}')
            
            # Update password and permissions (always do this)
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Superuser "{username}" password and permissions updated!')
            )
            self.stdout.write(f'📧 Email: {email}')
            self.stdout.write(f'🔑 Password: {"*" * len(password)}')
            self.stdout.write('🌐 You can now login to the admin panel')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error updating superuser: {e}')
            )
