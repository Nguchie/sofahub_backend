from django.core.management.base import BaseCommand
from products.models import ProductImage
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Clean up orphaned images (files without DB records or DB records without files)'

    def handle(self, *args, **options):
        self.stdout.write("🧹 CLEANING UP IMAGES")
        self.stdout.write("=" * 50)
        
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        
        if not os.path.exists(products_dir):
            self.stdout.write("❌ Products directory doesn't exist")
            return
        
        # Get all image files in products directory
        all_files = set(os.listdir(products_dir))
        image_files = {f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))}
        
        self.stdout.write(f"📂 Found {len(image_files)} image files in filesystem")
        
        # Get all image records from database
        db_images = ProductImage.objects.all()
        db_filenames = set()
        
        orphaned_records = []
        
        for img in db_images:
            filename = os.path.basename(img.image.name)
            db_filenames.add(filename)
            
            # Check if file exists
            full_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
            if not os.path.exists(full_path):
                orphaned_records.append((img.id, img.image.name))
        
        self.stdout.write(f"🗄️  Found {len(db_images)} image records in database")
        
        # Find orphaned files (files without DB records)
        orphaned_files = image_files - db_filenames
        
        # Report findings
        self.stdout.write(f"\n📊 ANALYSIS:")
        self.stdout.write(f"   Orphaned DB records (no file): {len(orphaned_records)}")
        self.stdout.write(f"   Orphaned files (no DB record): {len(orphaned_files)}")
        
        # Clean up orphaned DB records
        if orphaned_records:
            self.stdout.write(f"\n🗑️  CLEANING ORPHANED DB RECORDS:")
            for record_id, filename in orphaned_records:
                try:
                    ProductImage.objects.filter(id=record_id).delete()
                    self.stdout.write(f"   ✅ Deleted DB record ID {record_id}: {filename}")
                except Exception as e:
                    self.stdout.write(f"   ❌ Error deleting DB record {record_id}: {e}")
        
        # Report orphaned files (but don't delete - they might be in use)
        if orphaned_files:
            self.stdout.write(f"\n⚠️  ORPHANED FILES (not deleting automatically):")
            for filename in sorted(orphaned_files):
                self.stdout.write(f"   📄 {filename}")
            self.stdout.write(f"\n   Note: These files have no DB records. If they're not needed,")
            self.stdout.write(f"   delete them manually or they'll be used as fallback images.")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("✅ Cleanup completed!")

