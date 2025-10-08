from django.core.management.base import BaseCommand
from products.models import Product, ProductImage
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Debug image URLs and file paths'

    def handle(self, *args, **options):
        """Debug image issues step by step"""
        
        self.stdout.write('🔍 IMAGE DEBUGGING')
        self.stdout.write('=' * 50)
        
        # 1. Check settings
        self.stdout.write(f'\n📋 SETTINGS:')
        self.stdout.write(f'  MEDIA_URL: {settings.MEDIA_URL}')
        self.stdout.write(f'  MEDIA_ROOT: {settings.MEDIA_ROOT}')
        self.stdout.write(f'  DEBUG: {settings.DEBUG}')
        
        # 2. Check if media directory exists
        self.stdout.write(f'\n📁 MEDIA DIRECTORY:')
        if os.path.exists(settings.MEDIA_ROOT):
            self.stdout.write(f'  ✅ Exists: {settings.MEDIA_ROOT}')
            
            # List contents
            try:
                contents = os.listdir(settings.MEDIA_ROOT)
                self.stdout.write(f'  📂 Contents: {contents}')
                
                # Check products subdirectory
                products_path = os.path.join(settings.MEDIA_ROOT, 'products')
                if os.path.exists(products_path):
                    self.stdout.write(f'  ✅ Products dir exists: {products_path}')
                    product_files = os.listdir(products_path)
                    self.stdout.write(f'  📂 Product files: {product_files}')
                else:
                    self.stdout.write(f'  ❌ Products dir missing: {products_path}')
            except Exception as e:
                self.stdout.write(f'  ❌ Error: {e}')
        else:
            self.stdout.write(f'  ❌ Missing: {settings.MEDIA_ROOT}')
        
        # 3. Check database records
        self.stdout.write(f'\n🗄️ DATABASE:')
        products_with_images = Product.objects.filter(images__isnull=False).distinct()
        self.stdout.write(f'  Products with images: {products_with_images.count()}')
        
        if products_with_images.exists():
            for product in products_with_images:
                self.stdout.write(f'\n  📦 Product: {product.name}')
                images = product.images.all()
                
                for img in images:
                    self.stdout.write(f'    🖼️ Image: {img.image.name}')
                    self.stdout.write(f'    📁 Path: {img.image.path}')
                    self.stdout.write(f'    🌐 URL: {img.image.url}')
                    
                    # Check if file exists
                    if os.path.exists(img.image.path):
                        file_size = os.path.getsize(img.image.path)
                        self.stdout.write(f'    ✅ File exists: {file_size} bytes')
                        
                        # Test URL construction
                        base_url = 'https://sofahubbackend-production.up.railway.app'
                        full_url = f"{base_url}{img.image.url}"
                        self.stdout.write(f'    🔗 Full URL: {full_url}')
                    else:
                        self.stdout.write(f'    ❌ File missing: {img.image.path}')
        
        # 4. Test a specific image URL
        self.stdout.write(f'\n🧪 URL TEST:')
        if products_with_images.exists():
            product = products_with_images.first()
            image = product.images.first()
            if image:
                test_url = f"https://sofahubbackend-production.up.railway.app{image.image.url}"
                self.stdout.write(f'  Test URL: {test_url}')
                self.stdout.write(f'  File path: {image.image.path}')
                self.stdout.write(f'  File exists: {os.path.exists(image.image.path)}')
        
        self.stdout.write('\n' + '=' * 50)