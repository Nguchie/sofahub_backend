from django.core.management.base import BaseCommand
from products.models import Product, ProductImage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Test image upload functionality'

    def handle(self, *args, **options):
        self.stdout.write("🧪 TESTING IMAGE UPLOAD")
        self.stdout.write("=" * 50)
        
        # Check media directory
        media_root = settings.MEDIA_ROOT
        products_dir = os.path.join(media_root, 'products')
        
        self.stdout.write(f"📁 Media root: {media_root}")
        self.stdout.write(f"📁 Products dir: {products_dir}")
        self.stdout.write(f"📁 Products dir exists: {os.path.exists(products_dir)}")
        
        # Check permissions
        if os.path.exists(products_dir):
            self.stdout.write(f"📁 Products dir writable: {os.access(products_dir, os.W_OK)}")
        
        # Test creating a simple image
        try:
            # Create a simple test image (1x1 pixel PNG)
            test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            test_file = SimpleUploadedFile(
                "test_image.png",
                test_image_data,
                content_type="image/png"
            )
            
            self.stdout.write("✅ Test image created successfully")
            
            # Try to get a product to test with
            product = Product.objects.first()
            if not product:
                self.stdout.write("❌ No products found to test with")
                return
            
            self.stdout.write(f"📦 Testing with product: {product.name}")
            
            # Create ProductImage instance
            product_image = ProductImage(
                product=product,
                image=test_file,
                alt_text="Test image",
                is_primary=False,
                order=999
            )
            
            # Save it
            product_image.save()
            self.stdout.write(f"✅ Image saved successfully with ID: {product_image.id}")
            self.stdout.write(f"   Image name: {product_image.image.name}")
            
            # Check if file exists
            full_path = os.path.join(media_root, product_image.image.name)
            self.stdout.write(f"   Full path: {full_path}")
            self.stdout.write(f"   File exists: {os.path.exists(full_path)}")
            
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                self.stdout.write(f"   File size: {file_size} bytes")
            
            # Clean up
            product_image.delete()
            self.stdout.write("🗑️  Test image cleaned up")
            
        except Exception as e:
            self.stdout.write(f"❌ Error during upload test: {e}")
            import traceback
            self.stdout.write(f"❌ Traceback: {traceback.format_exc()}")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("✅ Upload test completed!")
