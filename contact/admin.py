from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']
    list_editable = ['is_read']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')

    def has_add_permission(self, request):
        """Staff cannot add contact messages (they come from the website)"""
        return False

    def has_change_permission(self, request, obj=None):
        """Staff can only mark messages as read, not edit content"""
        if request.user.is_superuser:
            return True
        # Staff can only change is_read field
        return True

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete contact messages"""
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        """Make message content readonly for staff users"""
        if not request.user.is_superuser:
            return ['name', 'email', 'subject', 'message', 'created_at']
        return ['created_at']
