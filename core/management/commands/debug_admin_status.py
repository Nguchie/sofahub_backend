from django.core.management.base import BaseCommand
from products.models import ProductImage
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Debug the image status function used in admin'

    def handle(self, *args, **options):
        self.stdout.write("🔍 DEBUGGING ADMIN IMAGE STATUS")
        self.stdout.write("=" * 50)
        
        images = ProductImage.objects.all()
        
        for img in images:
            self.stdout.write(f"\n🖼️  Image ID: {img.id}")
            self.stdout.write(f"   Image field: {img.image}")
            self.stdout.write(f"   Image name: {img.image.name if img.image else 'None'}")
            
            if img.image and img.image.name:
                full_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
                self.stdout.write(f"   Full path: {full_path}")
                self.stdout.write(f"   Path exists: {os.path.exists(full_path)}")
                
                if os.path.exists(full_path):
                    try:
                        file_size = os.path.getsize(full_path)
                        size_kb = file_size / 1024
                        self.stdout.write(f"   File size: {size_kb:.1f} KB")
                        self.stdout.write(f"   Status should be: ✓ {size_kb:.1f} KB")
                    except Exception as e:
                        self.stdout.write(f"   Error getting size: {e}")
                else:
                    self.stdout.write(f"   Status should be: ✗ File missing")
            else:
                self.stdout.write(f"   Status should be: - (no image)")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("✅ Debug completed!")
