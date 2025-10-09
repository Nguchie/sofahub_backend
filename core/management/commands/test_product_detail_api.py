from django.core.management.base import BaseCommand
from products.models import Product
from products.serializers import ProductSerializer
from django.test import RequestFactory
from django.conf import settings


class Command(BaseCommand):
    help = 'Test product detail API to see what data is returned'

    def handle(self, *args, **options):
        self.stdout.write("🧪 TESTING PRODUCT DETAIL API")
        self.stdout.write("=" * 50)
        
        # Get a product with images
        product = Product.objects.filter(images__isnull=False).first()
        
        if not product:
            self.stdout.write("❌ No products with images found!")
            return
            
        self.stdout.write(f"📦 Testing Product: {product.name}")
        self.stdout.write(f"   Slug: {product.slug}")
        self.stdout.write(f"   Images count: {product.images.count()}")
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get(f'/api/products/{product.slug}/')
        
        # Set the host to match production
        request.META['HTTP_HOST'] = 'sofahubbackend-production.up.railway.app'
        request.META['wsgi.url_scheme'] = 'https'
        
        # Serialize the product
        serializer = ProductSerializer(product, context={'request': request})
        data = serializer.data
        
        self.stdout.write(f"\n📊 SERIALIZED DATA:")
        self.stdout.write(f"   Product ID: {data.get('id')}")
        self.stdout.write(f"   Product Name: {data.get('name')}")
        self.stdout.write(f"   Images count in response: {len(data.get('images', []))}")
        
        # Check each image
        for i, image_data in enumerate(data.get('images', [])):
            self.stdout.write(f"\n🖼️  Image {i+1}:")
            self.stdout.write(f"   ID: {image_data.get('id')}")
            self.stdout.write(f"   URL: {image_data.get('image')}")
            self.stdout.write(f"   Alt text: {image_data.get('alt_text')}")
            self.stdout.write(f"   Is primary: {image_data.get('is_primary')}")
            self.stdout.write(f"   Order: {image_data.get('order')}")
        
        # Test the actual API URL
        api_url = f"https://sofahubbackend-production.up.railway.app/api/products/{product.slug}/"
        self.stdout.write(f"\n🌐 API URL: {api_url}")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("✅ Product detail API testing completed!")
