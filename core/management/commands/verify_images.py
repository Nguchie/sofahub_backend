from django.core.management.base import BaseCommand
from products.models import Product, ProductImage
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Verify image system health and report any issues'

    def handle(self, *args, **options):
        self.stdout.write("🔍 VERIFYING IMAGE SYSTEM")
        self.stdout.write("=" * 50)
        
        # Check products directory
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        if not os.path.exists(products_dir):
            self.stdout.write("❌ Products directory doesn't exist!")
            return
        
        self.stdout.write(f"✅ Products directory exists: {products_dir}")
        
        # Get all products
        products = Product.objects.filter(is_active=True)
        self.stdout.write(f"\n📦 Active Products: {products.count()}")
        
        products_with_images = 0
        products_without_images = 0
        total_images = 0
        working_images = 0
        broken_images = 0
        
        for product in products:
            images = product.images.all()
            
            if images.exists():
                products_with_images += 1
                
                for img in images:
                    total_images += 1
                    full_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
                    
                    if os.path.exists(full_path):
                        working_images += 1
                    else:
                        broken_images += 1
                        self.stdout.write(f"   ❌ {product.name}: Missing file {img.image.name}")
            else:
                products_without_images += 1
                self.stdout.write(f"   ⚠️  {product.name}: No images")
        
        # Summary
        self.stdout.write(f"\n📊 SUMMARY:")
        self.stdout.write(f"   Products with images: {products_with_images}")
        self.stdout.write(f"   Products without images: {products_without_images}")
        self.stdout.write(f"   Total image records: {total_images}")
        self.stdout.write(f"   ✅ Working images: {working_images}")
        self.stdout.write(f"   ❌ Broken images: {broken_images}")
        
        # Health score
        if total_images > 0:
            health_score = (working_images / total_images) * 100
            self.stdout.write(f"\n🏥 HEALTH SCORE: {health_score:.1f}%")
            
            if health_score == 100:
                self.stdout.write("   ✅ Perfect! All images are working.")
            elif health_score >= 80:
                self.stdout.write("   ⚠️  Good, but some images need attention.")
            else:
                self.stdout.write("   ❌ Poor! Many images are broken.")
        
        # Check filesystem
        all_files = os.listdir(products_dir)
        image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
        
        self.stdout.write(f"\n📂 Filesystem:")
        self.stdout.write(f"   Total files in products/: {len(image_files)}")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("✅ Verification completed!")

