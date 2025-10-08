from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'List all users in the database'

    def handle(self, *args, **options):
        """List all users with their permissions"""
        
        users = User.objects.all()
        
        if not users.exists():
            self.stdout.write('❌ No users found in database')
            return
        
        self.stdout.write('👥 Users in database:')
        self.stdout.write('-' * 50)
        
        for user in users:
            status = []
            if user.is_superuser:
                status.append('SUPERUSER')
            if user.is_staff:
                status.append('STAFF')
            if user.is_active:
                status.append('ACTIVE')
            else:
                status.append('INACTIVE')
            
            status_str = ', '.join(status)
            
            self.stdout.write(f'Username: {user.username}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Status: {status_str}')
            self.stdout.write(f'Last Login: {user.last_login or "Never"}')
            self.stdout.write('-' * 30)
