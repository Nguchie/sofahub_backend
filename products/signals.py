from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import ProductImage
import os

# Temporarily disable signals to debug upload issues
DISABLE_SIGNALS = True

if not DISABLE_SIGNALS:
    @receiver(post_delete, sender=ProductImage)
    def delete_image_file(sender, instance, **kwargs):
        """Delete the image file from filesystem when ProductImage is deleted"""
        if not instance.image or not instance.image.name:
            return
        
        try:
            from django.conf import settings
            full_path = os.path.join(settings.MEDIA_ROOT, instance.image.name)
            
            if os.path.isfile(full_path):
                os.remove(full_path)
                print(f"🗑️  Deleted image file: {full_path}")
            else:
                print(f"⚠️  Image file not found: {full_path}")
        except Exception as e:
            print(f"❌ Error deleting image file: {e}")
            # Don't raise the exception - just log it


    @receiver(pre_save, sender=ProductImage)
    def delete_old_image_on_update(sender, instance, **kwargs):
        """Delete old image file when a new image is uploaded to replace it"""
        if not instance.pk:
            return
        
        try:
            old_image = ProductImage.objects.get(pk=instance.pk).image
        except ProductImage.DoesNotExist:
            return

        # If image has changed, delete the old one
        new_image = instance.image
        if old_image and old_image != new_image:
            try:
                from django.conf import settings
                full_path = os.path.join(settings.MEDIA_ROOT, old_image.name)
                
                if os.path.isfile(full_path):
                    os.remove(full_path)
                    print(f"🗑️  Deleted old image file: {full_path}")
                else:
                    print(f"⚠️  Old image file not found: {full_path}")
            except Exception as e:
                print(f"❌ Error deleting old image file: {e}")
                # Don't raise the exception - just log it

