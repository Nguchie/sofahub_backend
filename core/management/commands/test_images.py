from django.core.management.base import BaseCommand
from products.models import Product, ProductImage
from django.conf import settings


class Command(BaseCommand):
    help = 'Test image URLs for products'

    def handle(self, *args, **options):
        """Test image URLs"""
        
        self.stdout.write('🖼️  Testing Product Images...')
        
        # Get products with images
        products_with_images = Product.objects.filter(images__isnull=False).distinct()
        
        if not products_with_images.exists():
            self.stdout.write('❌ No products with images found')
            return
        
        for product in products_with_images:
            self.stdout.write(f'\n📦 Product: {product.name}')
            
            images = product.images.all()
            for img in images:
                self.stdout.write(f'  🖼️  Image: {img.image.name}')
                self.stdout.write(f'  📁 Path: {img.image.path}')
                self.stdout.write(f'  🌐 URL: {img.image.url}')
                self.stdout.write(f'  🔗 Full URL: https://sofahubbackend-production.up.railway.app{img.image.url}')
                
                # Check if file exists
                import os
                if os.path.exists(img.image.path):
                    self.stdout.write(f'  ✅ File exists: {os.path.getsize(img.image.path)} bytes')
                else:
                    self.stdout.write(f'  ❌ File missing: {img.image.path}')
        
        self.stdout.write(f'\n📊 Media settings:')
        self.stdout.write(f'  MEDIA_URL: {settings.MEDIA_URL}')
        self.stdout.write(f'  MEDIA_ROOT: {settings.MEDIA_ROOT}')
        self.stdout.write(f'  DEBUG: {settings.DEBUG}')
