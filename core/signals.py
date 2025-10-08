from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=User)
def set_user_permissions(sender, instance, created, **kwargs):
    """Automatically set permissions when a user is created or updated"""
    
    # Only run for staff users who are not superusers
    if not instance.is_staff or instance.is_superuser:
        return
    
    # Only set permissions for new users or users with no permissions
    if created or instance.user_permissions.count() == 0:
        try:
            set_staff_permissions(instance)
        except Exception as e:
            # If there's an error, just log it and continue
            print(f"Warning: Could not set permissions for {instance.username}: {e}")


def set_staff_permissions(user):
    """Set appropriate permissions for staff users"""
    
    try:
        # Get content types for models staff can manage
        product_ct = ContentType.objects.get(app_label='products', model='product')
        product_image_ct = ContentType.objects.get(app_label='products', model='productimage')
        product_variation_ct = ContentType.objects.get(app_label='products', model='productvariation')
        contact_ct = ContentType.objects.get(app_label='contact', model='contactmessage')
        
        # Permissions for Products
        product_permissions = Permission.objects.filter(
            content_type__in=[product_ct, product_image_ct, product_variation_ct]
        )
        
        # Permissions for Contact
        contact_permissions = Permission.objects.filter(content_type=contact_ct)
        
        # Add all permissions
        all_permissions = product_permissions | contact_permissions
        user.user_permissions.set(all_permissions)
        
        print(f"✅ Set permissions for staff user: {user.username}")
        print(f"   - Product permissions: {product_permissions.count()}")
        print(f"   - Contact permissions: {contact_permissions.count()}")
        
    except ContentType.DoesNotExist as e:
        print(f"Warning: ContentType not found: {e}")
    except Exception as e:
        print(f"Warning: Error setting permissions: {e}")
