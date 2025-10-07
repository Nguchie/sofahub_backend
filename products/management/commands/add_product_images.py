from django.core.management.base import BaseCommand
from products.models import Product, ProductImage
from django.core.files.base import ContentFile
from PIL import Image
import io
import random


class Command(BaseCommand):
    help = 'Add placeholder images to products that don\'t have any'

    def handle(self, *args, **options):
        products_without_images = Product.objects.filter(images__isnull=True)
        
        if not products_without_images.exists():
            self.stdout.write(
                self.style.SUCCESS('All products already have images')
            )
            return

        self.stdout.write(f'Adding images to {products_without_images.count()} products...')

        for product in products_without_images:
            # Create a simple placeholder image
            img = Image.new('RGB', (400, 400), color=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
            
            # Add product name as text (simplified)
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_io.seek(0)
            
            # Create ProductImage
            image_file = ContentFile(img_io.getvalue(), name=f'{product.slug}_placeholder.jpg')
            
            product_image = ProductImage.objects.create(
                product=product,
                image=image_file,
                alt_text=f'{product.name} image',
                is_primary=True,  # Mark as primary
                order=0
            )
            
            self.stdout.write(f'  ✓ Added image to {product.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully added images to {products_without_images.count()} products')
        )
