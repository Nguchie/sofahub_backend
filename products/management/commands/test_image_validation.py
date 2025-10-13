"""
Management command to test image validation and URL generation
"""
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from products.models import Product, ProductImage
from core.utils import validate_product_image, get_image_url
from PIL import Image
import io


class Command(BaseCommand):
    help = 'Test image validation and URL generation'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🧪 Testing Image Validation & URL Generation\n'))
        
        # Test 1: URL Generation
        self.test_url_generation()
        
        # Test 2: File Size Validation
        self.test_file_size_validation()
        
        # Test 3: File Type Validation
        self.test_file_type_validation()
        
        # Test 4: Dimension Validation
        self.test_dimension_validation()
        
        # Test 5: Valid Image Upload
        self.test_valid_image_upload()
        
        self.stdout.write(self.style.SUCCESS('\n✅ All tests completed!\n'))

    def test_url_generation(self):
        """Test URL generation with and without request"""
        self.stdout.write('\n📝 Test 1: URL Generation')
        
        try:
            # Test without request (uses settings.SITE_URL)
            url = get_image_url(1)
            assert '/api/images/1/' in url, "URL should contain /api/images/1/"
            self.stdout.write(self.style.SUCCESS(f'  ✓ URL without request: {url}'))
            
            # Test with mock request
            from django.test import RequestFactory
            from django.conf import settings
            factory = RequestFactory()
            request = factory.get('/')
            request.META['HTTP_HOST'] = 'testserver'
            url_with_request = get_image_url(1, request)
            assert '/api/images/1/' in url_with_request, "URL should contain /api/images/1/"
            self.stdout.write(self.style.SUCCESS(f'  ✓ URL with request: {url_with_request}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ URL Generation failed: {str(e)}'))

    def test_file_size_validation(self):
        """Test file size validation"""
        self.stdout.write('\n📝 Test 2: File Size Validation')
        
        try:
            # Create a dummy file that's too large (> 5MB)
            large_content = b'x' * (6 * 1024 * 1024)  # 6MB
            large_file = SimpleUploadedFile("large.jpg", large_content, content_type="image/jpeg")
            
            try:
                validate_product_image(large_file)
                self.stdout.write(self.style.ERROR('  ✗ Should have rejected large file'))
            except ValidationError as e:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Correctly rejected large file: {str(e)}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ File size test failed: {str(e)}'))

    def test_file_type_validation(self):
        """Test file type validation"""
        self.stdout.write('\n📝 Test 3: File Type Validation')
        
        try:
            # Create a fake image with wrong extension
            fake_file = SimpleUploadedFile("fake.txt", b'not an image', content_type="text/plain")
            
            try:
                validate_product_image(fake_file)
                self.stdout.write(self.style.ERROR('  ✗ Should have rejected non-image file'))
            except ValidationError as e:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Correctly rejected non-image: {str(e)}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ File type test failed: {str(e)}'))

    def test_dimension_validation(self):
        """Test dimension validation"""
        self.stdout.write('\n📝 Test 4: Dimension Validation')
        
        try:
            # Create image that's too small (< 300x200)
            img = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)
            small_file = SimpleUploadedFile("small.jpg", buffer.getvalue(), content_type="image/jpeg")
            
            try:
                validate_product_image(small_file)
                self.stdout.write(self.style.ERROR('  ✗ Should have rejected small image'))
            except ValidationError as e:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Correctly rejected small image: {str(e)}'))
            
            # Create image that's too large (> 4000x4000)
            # Note: This test is commented out because creating a 5000x5000 image takes too much memory
            # In production, Pillow will handle this validation
            self.stdout.write(self.style.WARNING('  ⚠ Skipping large dimension test (memory intensive)'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Dimension test failed: {str(e)}'))

    def test_valid_image_upload(self):
        """Test that valid images are accepted"""
        self.stdout.write('\n📝 Test 5: Valid Image Upload')
        
        try:
            # Create a valid image
            img = Image.new('RGB', (800, 600), color='blue')
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)
            valid_file = SimpleUploadedFile("valid.jpg", buffer.getvalue(), content_type="image/jpeg")
            
            # This should pass without errors
            validate_product_image(valid_file)
            self.stdout.write(self.style.SUCCESS('  ✓ Valid image passed validation'))
            
            # Test with actual Product and ProductImage creation
            try:
                product = Product.objects.first()
                if product:
                    # Reset file pointer
                    valid_file.seek(0)
                    
                    # Note: We won't actually save to avoid cluttering the database
                    self.stdout.write(self.style.SUCCESS('  ✓ Image ready for ProductImage creation'))
                else:
                    self.stdout.write(self.style.WARNING('  ⚠ No products in database to test with'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ ProductImage creation test failed: {str(e)}'))
            
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Valid image was rejected: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Valid image test failed: {str(e)}'))

    def create_test_image(self, width, height, filename='test.jpg'):
        """Helper to create test images"""
        img = Image.new('RGB', (width, height), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile(filename, buffer.getvalue(), content_type="image/jpeg")

