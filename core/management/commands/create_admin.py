from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Create admin user for deployment'

    def handle(self, *args, **options):
        # Check if admin user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )
            return

        # Create admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@sofahub.com',
            password='admin123'  # Change this password!
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin user: {admin_user.username}')
        )
        self.stdout.write(
            self.style.WARNING('IMPORTANT: Change the admin password after first login!')
        )
