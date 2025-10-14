from django.core.management.base import BaseCommand
from products.models import ProductImage
from blog.models import BlogPost
from core.utils import optimize_image
import os


class Command(BaseCommand):
    help = 'Process images in background - optimize existing images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Number of images to process (default: 10)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without actually doing it'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        
        self.stdout.write(f"Processing up to {limit} images...")
        
        # Process ProductImages
        product_images = ProductImage.objects.filter(image__isnull=False)[:limit]
        processed_count = 0
        
        for img in product_images:
            if dry_run:
                self.stdout.write(f"Would process: {img.image.name}")
                continue
                
            try:
                # Check if image file exists
                if not os.path.exists(img.image.path):
                    self.stdout.write(f"⚠️ File not found: {img.image.name}")
                    continue
                
                # Optimize the image
                optimized = optimize_image(img.image, max_width=2000, max_height=2000, quality=85)
                
                # Save the optimized version
                img.image = optimized
                img.save()
                
                processed_count += 1
                self.stdout.write(f"✅ Processed: {img.image.name}")
                
            except Exception as e:
                self.stdout.write(f"❌ Failed to process {img.image.name}: {e}")
        
        # Process BlogPost featured images
        blog_posts = BlogPost.objects.filter(featured_image__isnull=False)[:limit//2]
        
        for post in blog_posts:
            if dry_run:
                self.stdout.write(f"Would process blog image: {post.featured_image.name}")
                continue
                
            try:
                # Check if image file exists
                if not os.path.exists(post.featured_image.path):
                    self.stdout.write(f"⚠️ Blog file not found: {post.featured_image.name}")
                    continue
                
                # Optimize the image
                optimized = optimize_image(post.featured_image, max_width=1920, max_height=1920, quality=85)
                
                # Save the optimized version
                post.featured_image = optimized
                post.save()
                
                processed_count += 1
                self.stdout.write(f"✅ Processed blog image: {post.featured_image.name}")
                
            except Exception as e:
                self.stdout.write(f"❌ Failed to process blog image {post.featured_image.name}: {e}")
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run complete. Would process {len(product_images) + len(blog_posts)} images."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Successfully processed {processed_count} images."))
