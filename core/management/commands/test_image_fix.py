from django.core.management.base import BaseCommand
from products.models import ProductImage
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Test the image fix by checking URLs and file existence'

    def handle(self, *args, **options):
        self.stdout.write("🧪 TESTING IMAGE FIX - BULLETPROOF VERSION")
        self.stdout.write("=" * 50)
        
        # Get all product images
        images = ProductImage.objects.all()
        self.stdout.write(f"Found {images.count()} product images")
        
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        self.stdout.write(f"Products directory: {products_dir}")
        
        if os.path.exists(products_dir):
            all_files = os.listdir(products_dir)
            self.stdout.write(f"Files in products directory: {len(all_files)}")
            
            for image in images[:5]:  # Test first 5 images
                self.stdout.write(f"\n🖼️  Image ID: {image.id}")
                self.stdout.write(f"   DB filename: {image.image.name}")
                
                # Test ID-based URL
                id_url = f"https://sofahubbackend-production.up.railway.app/api/images/{image.id}/"
                self.stdout.write(f"   ID URL: {id_url}")
                
                # Check if file exists
                filename = os.path.basename(image.image.name)
                exact_path = os.path.join(products_dir, filename)
                
                if os.path.exists(exact_path):
                    self.stdout.write(f"   ✅ Exact file exists: {filename}")
                else:
                    self.stdout.write(f"   ❌ Exact file missing: {filename}")
                    
                    # Look for similar files
                    base_name = filename.split('_')[0] if '_' in filename else filename.split('.')[0]
                    similar_files = [f for f in all_files if f.startswith(base_name) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
                    
                    if similar_files:
                        self.stdout.write(f"   🔍 Found similar files: {similar_files[:3]}")
                    else:
                        self.stdout.write(f"   ❌ No similar files found")
        else:
            self.stdout.write("❌ Products directory doesn't exist")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("✅ Test completed!")
