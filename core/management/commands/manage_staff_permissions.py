from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Manage staff user permissions (superuser only)'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to manage permissions for')
        parser.add_argument('--list', action='store_true', help='List all staff users and their permissions')
        parser.add_argument('--add-permission', type=str, help='Add a specific permission (format: app.model.action)')
        parser.add_argument('--remove-permission', type=str, help='Remove a specific permission')
        parser.add_argument('--reset', action='store_true', help='Reset to default staff permissions')
        parser.add_argument('--grant-all', action='store_true', help='Grant all permissions (make superuser-like)')

    def handle(self, *args, **options):
        """Manage staff permissions"""
        
        if options['list']:
            self.list_staff_users()
            return
        
        username = options['username']
        if not username:
            self.stdout.write(
                self.style.ERROR('❌ Please provide --username')
            )
            return
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ User "{username}" not found')
            )
            return
        
        if not user.is_staff:
            self.stdout.write(
                self.style.ERROR(f'❌ User "{username}" is not a staff user')
            )
            return
        
        if user.is_superuser:
            self.stdout.write(
                self.style.WARNING(f'⚠️  User "{username}" is a superuser - they already have all permissions')
            )
            return
        
        if options['reset']:
            self.reset_to_default_permissions(user)
        elif options['grant_all']:
            self.grant_all_permissions(user)
        elif options['add_permission']:
            self.add_specific_permission(user, options['add_permission'])
        elif options['remove_permission']:
            self.remove_specific_permission(user, options['remove_permission'])
        else:
            self.show_user_permissions(user)

    def list_staff_users(self):
        """List all staff users"""
        staff_users = User.objects.filter(is_staff=True)
        
        self.stdout.write('👥 Staff Users:')
        self.stdout.write('-' * 50)
        
        for user in staff_users:
            status = 'SUPERUSER' if user.is_superuser else 'STAFF'
            permissions_count = user.user_permissions.count()
            
            self.stdout.write(f'Username: {user.username}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Status: {status}')
            self.stdout.write(f'Permissions: {permissions_count}')
            self.stdout.write('-' * 30)

    def show_user_permissions(self, user):
        """Show current permissions for a user"""
        permissions = user.user_permissions.all()
        
        self.stdout.write(f'🔍 Permissions for {user.username}:')
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

    def reset_to_default_permissions(self, user):
        """Reset user to default staff permissions"""
        from core.signals import set_staff_permissions
        
        set_staff_permissions(user)
        self.stdout.write(
            self.style.SUCCESS(f'✅ Reset {user.username} to default staff permissions')
        )

    def grant_all_permissions(self, user):
        """Grant all permissions to user"""
        all_permissions = Permission.objects.all()
        user.user_permissions.set(all_permissions)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Granted all permissions to {user.username}')
        )
        self.stdout.write('⚠️  Note: This makes them superuser-like but not actually superuser')

    def add_specific_permission(self, user, permission_string):
        """Add a specific permission"""
        try:
            app_label, model, action = permission_string.split('.')
            ct = ContentType.objects.get(app_label=app_label, model=model)
            perm = Permission.objects.get(content_type=ct, codename=f'{action}_{model}')
            
            user.user_permissions.add(perm)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Added permission: {permission_string}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error adding permission: {e}')
            )

    def remove_specific_permission(self, user, permission_string):
        """Remove a specific permission"""
        try:
            app_label, model, action = permission_string.split('.')
            ct = ContentType.objects.get(app_label=app_label, model=model)
            perm = Permission.objects.get(content_type=ct, codename=f'{action}_{model}')
            
            user.user_permissions.remove(perm)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Removed permission: {permission_string}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error removing permission: {e}')
            )
