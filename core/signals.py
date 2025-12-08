from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Redirect


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
        order_ct = ContentType.objects.get(app_label='orders', model='order')
        order_item_ct = ContentType.objects.get(app_label='orders', model='orderitem')
        cart_ct = ContentType.objects.get(app_label='cart', model='cart')
        cart_item_ct = ContentType.objects.get(app_label='cart', model='cartitem')
        
        # Permissions for Products
        product_permissions = Permission.objects.filter(
            content_type__in=[product_ct, product_image_ct, product_variation_ct]
        )
        
        # Permissions for Contact
        contact_permissions = Permission.objects.filter(content_type=contact_ct)
        
        # Permissions for Orders (view and change only)
        order_permissions = Permission.objects.filter(
            content_type__in=[order_ct, order_item_ct]
        ).exclude(codename__contains='delete')  # Exclude delete permissions
        
        # Permissions for Cart (view only)
        cart_permissions = Permission.objects.filter(
            content_type__in=[cart_ct, cart_item_ct]
        ).filter(codename__contains='view')  # Only view permissions
        
        # Add all permissions
        all_permissions = product_permissions | contact_permissions | order_permissions | cart_permissions
        user.user_permissions.set(all_permissions)
        
        print(f"✅ Set permissions for staff user: {user.username}")
        print(f"   - Product permissions: {product_permissions.count()}")
        print(f"   - Contact permissions: {contact_permissions.count()}")
        print(f"   - Order permissions: {order_permissions.count()}")
        print(f"   - Cart permissions: {cart_permissions.count()}")
        
    except ContentType.DoesNotExist as e:
        print(f"Warning: ContentType not found: {e}")
    except Exception as e:
        print(f"Warning: Error setting permissions: {e}")


# Redirect signal handlers for slug changes
def create_redirect_if_slug_changed(instance, old_slug, new_slug, redirect_type):
    """Helper function to create a redirect when a slug changes"""
    if old_slug and new_slug and old_slug != new_slug:
        # Determine the path prefix based on redirect type
        path_prefix_map = {
            'product': '/product/',
            'category': '/category/',
            'blog': '/blog/',
        }
        path_prefix = path_prefix_map.get(redirect_type, '/')
        
        old_path = f"{path_prefix}{old_slug}"
        new_path = f"{path_prefix}{new_slug}"
        
        # Create redirect if it doesn't already exist
        redirect, created = Redirect.objects.get_or_create(
            old_path=old_path,
            defaults={
                'new_path': new_path,
                'redirect_type': redirect_type,
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Created redirect: {old_path} → {new_path}")
        elif redirect.new_path != new_path:
            # Update redirect if path changed again
            redirect.new_path = new_path
            redirect.save()
            print(f"✅ Updated redirect: {old_path} → {new_path}")


# Store old slugs before save
_product_old_slugs = {}
_category_old_slugs = {}
_blog_old_slugs = {}


@receiver(pre_save, sender='products.Product')
def store_product_old_slug(sender, instance, **kwargs):
    """Store old slug before product save"""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            _product_old_slugs[instance.pk] = old_instance.slug
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender='products.Product')
def handle_product_slug_change(sender, instance, created, **kwargs):
    """Create redirect when product slug changes"""
    if not created and instance.pk in _product_old_slugs:
        old_slug = _product_old_slugs[instance.pk]
        create_redirect_if_slug_changed(instance, old_slug, instance.slug, 'product')
        del _product_old_slugs[instance.pk]


@receiver(pre_save, sender='products.RoomCategory')
def store_category_old_slug(sender, instance, **kwargs):
    """Store old slug before category save"""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            _category_old_slugs[instance.pk] = old_instance.slug
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender='products.RoomCategory')
def handle_category_slug_change(sender, instance, created, **kwargs):
    """Create redirect when category slug changes"""
    if not created and instance.pk in _category_old_slugs:
        old_slug = _category_old_slugs[instance.pk]
        create_redirect_if_slug_changed(instance, old_slug, instance.slug, 'category')
        del _category_old_slugs[instance.pk]


@receiver(pre_save, sender='blog.BlogPost')
def store_blog_old_slug(sender, instance, **kwargs):
    """Store old slug before blog post save"""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            _blog_old_slugs[instance.pk] = old_instance.slug
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender='blog.BlogPost')
def handle_blog_slug_change(sender, instance, created, **kwargs):
    """Create redirect when blog post slug changes"""
    if not created and instance.pk in _blog_old_slugs:
        old_slug = _blog_old_slugs[instance.pk]
        create_redirect_if_slug_changed(instance, old_slug, instance.slug, 'blog')
        del _blog_old_slugs[instance.pk]
