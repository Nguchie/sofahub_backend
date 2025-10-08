from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html


class UserAdmin(BaseUserAdmin):
    """Custom User admin with better permission management"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'permission_count', 'last_login']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': 'Staff users automatically get Product & Contact permissions. Superusers can modify permissions manually.'
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'description': 'Check "Staff status" to give admin access. Check "Superuser status" for full control.'
        }),
    )
    
    def permission_count(self, obj):
        """Show number of permissions"""
        count = obj.user_permissions.count()
        if obj.is_superuser:
            return format_html('<span style="color: green; font-weight: bold;">Superuser (All)</span>')
        elif count > 0:
            return format_html('<span style="color: blue;">{} permissions</span>', count)
        else:
            return format_html('<span style="color: gray;">No permissions</span>')
    
    permission_count.short_description = 'Permissions'
    
    def save_model(self, request, obj, form, change):
        """Override save to show helpful messages"""
        super().save_model(request, obj, form, change)
        
        if obj.is_staff and not obj.is_superuser:
            self.message_user(
                request, 
                f"✅ {obj.username} is now a staff user with automatic Product & Contact permissions",
                level='SUCCESS'
            )
        elif obj.is_superuser:
            self.message_user(
                request, 
                f"✅ {obj.username} is now a superuser with full admin access",
                level='SUCCESS'
            )
        elif not obj.is_staff:
            self.message_user(
                request, 
                f"ℹ️ {obj.username} is a regular user with no admin access",
                level='INFO'
            )


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
