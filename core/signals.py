from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=User)
def set_user_permissions(sender, instance, created, **kwargs):
    """Automatically set permissions when a user is created or updated"""
    
    if created:
        # New user created
        if instance.is_staff and not instance.is_superuser:
            # Staff user - give them permissions for Products and Contact
            set_staff_permissions(instance)
        elif instance.is_superuser:
            # Superuser - they already have all permissions
            pass
    else:
        # Existing user updated
        if instance.is_staff and not instance.is_superuser:
            # Only set default permissions if user has no custom permissions
            # This allows superusers to manually override permissions
            if instance.user_permissions.count() == 0:
                set_staff_permissions(instance)
        elif not instance.is_staff:
            # Remove all permissions if user is no longer staff
            instance.user_permissions.clear()


def set_staff_permissions(user):
    """Set appropriate permissions for staff users"""
    
    # Get content types for models staff can manage
    product_ct = ContentType.objects.get_for_model('products.Product')
    product_image_ct = ContentType.objects.get_for_model('products.ProductImage')
    product_variation_ct = ContentType.objects.get_for_model('products.ProductVariation')
    contact_ct = ContentType.objects.get_for_model('contact.ContactMessage')
    
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
