from django.core.management.base import BaseCommand
from products.models import Product, ProductImage
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


class Command(BaseCommand):
    help = 'Test image upload functionality for new products'

    def handle(self, *args, **options):
        """Test that image uploads work correctly"""
        
        self.stdout.write('🧪 Testing image upload functionality...')
        
        # Create a test product
        test_product = Product.objects.create(
            name='Test Product for Image Upload',
            slug='test-product-image-upload',
            description='This is a test product to verify image uploads work',
            base_price=1000.00,
            is_active=True
        )
        
        # Create a test image
        img = Image.new('RGB', (400, 400), color='lightblue')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG', quality=85)
        img_io.seek(0)
        
        # Create uploaded file
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            img_io.getvalue(),
            content_type='image/jpeg'
        )
        
        # Create ProductImage
        product_image = ProductImage.objects.create(
            product=test_product,
            image=image_file,
            alt_text='Test image for upload verification',
            is_primary=True,
            order=0
        )
        
        # Test URL generation
        from products.serializers import ProductImageSerializer
        serializer = ProductImageSerializer(product_image)
        image_url = serializer.data['image']
        
        self.stdout.write(f'✅ Test product created: {test_product.name}')
        self.stdout.write(f'✅ Test image uploaded: {product_image.image.name}')
        self.stdout.write(f'✅ Image URL generated: {image_url}')
        
        # Clean up test data
        test_product.delete()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Image upload functionality test completed successfully!')
        )
        self.stdout.write('📝 New product image uploads should work correctly in production.')
