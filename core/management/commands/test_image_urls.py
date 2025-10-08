from django.core.management.base import BaseCommand
from django.conf import settings
from django.test import RequestFactory
from products.models import Product, ProductImage
import os


class Command(BaseCommand):
    help = 'Test image URL generation'

    def handle(self, *args, **options):
        """Test image URL generation"""
        
        self.stdout.write('🧪 TESTING IMAGE URL GENERATION')
        self.stdout.write('=' * 40)
        
        # Test 1: Check if products with images exist
        products = Product.objects.filter(images__isnull=False).distinct()
        self.stdout.write(f'Products with images: {products.count()}')
        
        if not products.exists():
            self.stdout.write('❌ No products with images found!')
            return
        
        # Test 2: Check first product's images
        product = products.first()
        self.stdout.write(f'\n📦 Testing product: {product.name}')
        
        images = product.images.all()
        self.stdout.write(f'Images count: {images.count()}')
        
        for img in images:
            self.stdout.write(f'\n🖼️ Image: {img.image.name}')
            self.stdout.write(f'File path: {img.image.path}')
            self.stdout.write(f'File URL: {img.image.url}')
            
            # Test if file exists
            if os.path.exists(img.image.path):
                file_size = os.path.getsize(img.image.path)
                self.stdout.write(f'✅ File exists: {file_size} bytes')
            else:
                self.stdout.write(f'❌ File missing: {img.image.path}')
            
            # Test URL generation with request context
            factory = RequestFactory()
            request = factory.get('/')
            request.META['HTTP_HOST'] = 'sofahubbackend-production.up.railway.app'
            request.META['wsgi.url_scheme'] = 'https'
            
            full_url = request.build_absolute_uri(img.image.url)
            self.stdout.write(f'🔗 Full URL: {full_url}')
            
            # Test serializer
            from products.serializers import ProductImageSerializer
            serializer = ProductImageSerializer(img, context={'request': request})
            serialized_url = serializer.data.get('image')
            self.stdout.write(f'📡 Serialized URL: {serialized_url}')
        
        # Test 3: Check Django settings
        self.stdout.write(f'\n⚙️ Django Settings:')
        self.stdout.write(f'MEDIA_URL: {settings.MEDIA_URL}')
        self.stdout.write(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
        self.stdout.write(f'DEBUG: {settings.DEBUG}')
        
        # Test 4: Check if media directory exists
        if os.path.exists(settings.MEDIA_ROOT):
            self.stdout.write(f'✅ Media directory exists')
            contents = os.listdir(settings.MEDIA_ROOT)
            self.stdout.write(f'Contents: {contents}')
        else:
            self.stdout.write(f'❌ Media directory missing')
