from django.core.management.base import BaseCommand
from products.models import Product
from products.serializers import ProductSerializer
from django.test import RequestFactory
from django.conf import settings


class Command(BaseCommand):
    help = 'Test product detail API to see all images being returned'

    def handle(self, *args, **options):
        self.stdout.write("🧪 TESTING PRODUCT IMAGES API")
        self.stdout.write("=" * 50)
        
        # Get a product with multiple images
        product = Product.objects.filter(images__isnull=False).prefetch_related('images').first()
        
        if not product:
            self.stdout.write("❌ No products with images found!")
            return
            
        self.stdout.write(f"📦 Testing Product: {product.name}")
        self.stdout.write(f"   Slug: {product.slug}")
        self.stdout.write(f"   Total images in DB: {product.images.count()}")
        
        # Show all images in database
        self.stdout.write(f"\n🗄️  ALL IMAGES IN DATABASE:")
        for i, img in enumerate(product.images.all().order_by('order', 'id')):
            self.stdout.write(f"   {i+1}. ID: {img.id}")
            self.stdout.write(f"      Filename: {img.image.name}")
            self.stdout.write(f"      Is Primary: {img.is_primary}")
            self.stdout.write(f"      Order: {img.order}")
            self.stdout.write(f"      Alt Text: {img.alt_text}")
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get(f'/api/products/{product.slug}/')
        request.META['HTTP_HOST'] = 'sofahubbackend-production.up.railway.app'
        request.META['wsgi.url_scheme'] = 'https'
        
        # Serialize the product
        serializer = ProductSerializer(product, context={'request': request})
        data = serializer.data
        
        self.stdout.write(f"\n📊 API RESPONSE:")
        self.stdout.write(f"   Product ID: {data.get('id')}")
        self.stdout.write(f"   Product Name: {data.get('name')}")
        self.stdout.write(f"   Images count in API response: {len(data.get('images', []))}")
        
        # Show all images in API response
        self.stdout.write(f"\n🌐 IMAGES IN API RESPONSE:")
        for i, image_data in enumerate(data.get('images', [])):
            self.stdout.write(f"   {i+1}. ID: {image_data.get('id')}")
            self.stdout.write(f"      URL: {image_data.get('image')}")
            self.stdout.write(f"      Alt text: {image_data.get('alt_text')}")
            self.stdout.write(f"      Is primary: {image_data.get('is_primary')}")
            self.stdout.write(f"      Order: {image_data.get('order')}")
        
        # Test the actual API URL
        api_url = f"https://sofahubbackend-production.up.railway.app/api/products/{product.slug}/"
        self.stdout.write(f"\n🔗 API URL: {api_url}")
        
        # Check if images are ordered correctly
        db_images = product.images.all().order_by('order', 'id')
        api_images = data.get('images', [])
        
        self.stdout.write(f"\n🔍 ORDERING CHECK:")
        self.stdout.write(f"   DB order: {[f'{img.id}(order:{img.order})' for img in db_images]}")
        self.stdout.write(f"   API order: {[f'{img.get('id')}(order:{img.get('order')})' for img in api_images]}")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("✅ Product images API testing completed!")
