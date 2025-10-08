from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Show user permissions (for debugging)'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to check')

    def handle(self, *args, **options):
        """Show user permissions"""
        
        if options['username']:
            try:
                user = User.objects.get(username=options['username'])
                self.show_user_permissions(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ User "{options["username"]}" not found')
                )
        else:
            # Show all users
            users = User.objects.all()
            self.stdout.write('👥 All Users:')
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
                permissions_count = user.user_permissions.count()
                
                self.stdout.write(f'Username: {user.username}')
                self.stdout.write(f'Email: {user.email}')
                self.stdout.write(f'Status: {status_str}')
                self.stdout.write(f'Permissions: {permissions_count}')
                self.stdout.write('-' * 30)

    def show_user_permissions(self, user):
        """Show permissions for a specific user"""
        permissions = user.user_permissions.all()
        
        self.stdout.write(f'🔍 Permissions for {user.username}:')
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'Staff: {user.is_staff}')
        self.stdout.write(f'Superuser: {user.is_superuser}')
        self.stdout.write(f'Active: {user.is_active}')
        self.stdout.write('-' * 50)
        
        if not permissions:
            self.stdout.write('No permissions assigned')
            return
        
        # Group by content type
        by_content_type = {}
        for perm in permissions:
            ct_name = f"{perm.content_type.app_label}.{perm.content_type.model}"
            if ct_name not in by_content_type:
                by_content_type[ct_name] = []
            by_content_type[ct_name].append(perm.name)
        
        for ct_name, perms in by_content_type.items():
            self.stdout.write(f'{ct_name}:')
            for perm in perms:
                self.stdout.write(f'  - {perm}')
            self.stdout.write('')
