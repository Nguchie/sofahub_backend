from django.core.management.base import BaseCommand
from products.models import ProductImage
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Fix image filename mismatch between database and filesystem'

    def handle(self, *args, **options):
        """Fix the filename mismatch"""
        
        self.stdout.write('🔧 FIXING IMAGE FILENAME MISMATCH')
        self.stdout.write('=' * 50)
        
        # Get all product images
        images = ProductImage.objects.all()
        self.stdout.write(f'Found {images.count()} images in database')
        
        fixed_count = 0
        
        for img in images:
            db_filename = img.image.name
            db_path = os.path.join(settings.MEDIA_ROOT, db_filename)
            
            # Check if file exists with database name
            if os.path.exists(db_path):
                self.stdout.write(f'✅ {db_filename} - File exists')
                continue
            
            # File doesn't exist, try to find it without suffix
            base_name = db_filename.split('_')[-1]  # Get the part after last underscore
            if '.' in base_name:
                # Remove the random suffix (everything after the last underscore before extension)
                parts = db_filename.split('_')
                if len(parts) > 1:
                    # Reconstruct filename without the random suffix
                    filename_without_suffix = '_'.join(parts[:-1]) + '.' + base_name.split('.')[-1]
                    alt_path = os.path.join(settings.MEDIA_ROOT, filename_without_suffix)
                    
                    if os.path.exists(alt_path):
                        self.stdout.write(f'🔧 {db_filename} -> {filename_without_suffix}')
                        
                        # Update the database record
                        img.image.name = filename_without_suffix
                        img.save()
                        fixed_count += 1
                    else:
                        self.stdout.write(f'❌ {db_filename} - No matching file found')
                else:
                    self.stdout.write(f'❌ {db_filename} - Cannot parse filename')
            else:
                self.stdout.write(f'❌ {db_filename} - Invalid filename format')
        
        self.stdout.write(f'\n✅ Fixed {fixed_count} image records')
        self.stdout.write('=' * 50)
