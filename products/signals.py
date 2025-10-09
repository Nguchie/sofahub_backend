from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import ProductImage
import os


@receiver(post_delete, sender=ProductImage)
def delete_image_file(sender, instance, **kwargs):
    """Delete the image file from filesystem when ProductImage is deleted"""
    if instance.image:
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
                print(f"🗑️  Deleted image file: {instance.image.path}")
        except Exception as e:
            print(f"❌ Error deleting image file: {e}")


@receiver(pre_save, sender=ProductImage)
def delete_old_image_on_update(sender, instance, **kwargs):
    """Delete old image file when a new image is uploaded to replace it"""
    if not instance.pk:
        return False

    try:
        old_image = ProductImage.objects.get(pk=instance.pk).image
    except ProductImage.DoesNotExist:
        return False

    # If image has changed, delete the old one
    new_image = instance.image
    if old_image and old_image != new_image:
        try:
            if os.path.isfile(old_image.path):
                os.remove(old_image.path)
                print(f"🗑️  Deleted old image file: {old_image.path}")
        except Exception as e:
            print(f"❌ Error deleting old image file: {e}")

