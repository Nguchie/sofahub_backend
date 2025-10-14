from django.core.management.base import BaseCommand
from products.models import ProductImage, RoomCategory
from blog.models import BlogPost
from core.utils import optimize_image
from django.core.files.base import File
import os


class Command(BaseCommand):
    help = 'Optimize all existing images in the database to reduce storage costs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be optimized without actually doing it',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['products', 'blog', 'categories', 'all'],
            default='all',
            help='Which image type to optimize (default: all)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        image_type = options['type']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        total_before = 0
        total_after = 0
        count = 0
        
        # Optimize Product Images
        if image_type in ['products', 'all']:
            self.stdout.write(self.style.SUCCESS('\n📸 Optimizing Product Images...'))
            before, after, img_count = self._optimize_product_images(dry_run)
            total_before += before
            total_after += after
            count += img_count
        
        # Optimize Blog Images
        if image_type in ['blog', 'all']:
            self.stdout.write(self.style.SUCCESS('\n📝 Optimizing Blog Images...'))
            before, after, img_count = self._optimize_blog_images(dry_run)
            total_before += before
            total_after += after
            count += img_count
        
        # Optimize Category Images
        if image_type in ['categories', 'all']:
            self.stdout.write(self.style.SUCCESS('\n🏷️ Optimizing Category Images...'))
            before, after, img_count = self._optimize_category_images(dry_run)
            total_before += before
            total_after += after
            count += img_count
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('OPTIMIZATION SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Total images processed: {count}')
        self.stdout.write(f'Total size before: {total_before / (1024*1024):.2f} MB')
        self.stdout.write(f'Total size after: {total_after / (1024*1024):.2f} MB')
        
        if total_before > 0:
            savings = ((total_before - total_after) / total_before) * 100
            saved_mb = (total_before - total_after) / (1024*1024)
            self.stdout.write(self.style.SUCCESS(f'Space saved: {saved_mb:.2f} MB ({savings:.1f}%)'))
            
            # Estimate cost savings
            saved_gb = saved_mb / 1024
            monthly_savings = saved_gb * 0.25  # $0.25 per GB per month
            self.stdout.write(self.style.SUCCESS(f'💰 Estimated monthly savings: ${monthly_savings:.2f}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️ This was a DRY RUN. Run without --dry-run to actually optimize.'))

    def _optimize_product_images(self, dry_run):
        """Optimize all product images"""
        total_before = 0
        total_after = 0
        count = 0
        
        product_images = ProductImage.objects.all()
        
        for img_obj in product_images:
            if not img_obj.image:
                continue
            
            try:
                image_path = img_obj.image.path
                if not os.path.exists(image_path):
                    continue
                
                # Get original size
                original_size = os.path.getsize(image_path)
                total_before += original_size
                
                if not dry_run:
                    # Optimize the image
                    with open(image_path, 'rb') as f:
                        optimized = optimize_image(f, max_width=2000, max_height=2000, quality=85)
                        img_obj.image.save(
                            os.path.basename(image_path),
                            File(optimized),
                            save=False  # Don't trigger save() again
                        )
                        img_obj.save()
                    
                    # Get new size
                    new_size = os.path.getsize(img_obj.image.path)
                    total_after += new_size
                    savings = ((original_size - new_size) / original_size) * 100
                    
                    self.stdout.write(
                        f'  ✅ {img_obj.product.name}: '
                        f'{original_size/1024:.1f}KB → {new_size/1024:.1f}KB '
                        f'(saved {savings:.1f}%)'
                    )
                else:
                    total_after += original_size * 0.3  # Estimate 70% savings
                    self.stdout.write(f'  📋 Would optimize: {img_obj.product.name} ({original_size/1024:.1f}KB)')
                
                count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error with {img_obj}: {e}'))
        
        return total_before, total_after, count

    def _optimize_blog_images(self, dry_run):
        """Optimize all blog featured images"""
        total_before = 0
        total_after = 0
        count = 0
        
        blog_posts = BlogPost.objects.exclude(featured_image='')
        
        for post in blog_posts:
            if not post.featured_image:
                continue
            
            try:
                image_path = post.featured_image.path
                if not os.path.exists(image_path):
                    continue
                
                # Get original size
                original_size = os.path.getsize(image_path)
                total_before += original_size
                
                if not dry_run:
                    # Optimize the image
                    with open(image_path, 'rb') as f:
                        optimized = optimize_image(f, max_width=1920, max_height=1920, quality=85)
                        post.featured_image.save(
                            os.path.basename(image_path),
                            File(optimized),
                            save=False
                        )
                        post.save()
                    
                    # Get new size
                    new_size = os.path.getsize(post.featured_image.path)
                    total_after += new_size
                    savings = ((original_size - new_size) / original_size) * 100
                    
                    self.stdout.write(
                        f'  ✅ {post.title}: '
                        f'{original_size/1024:.1f}KB → {new_size/1024:.1f}KB '
                        f'(saved {savings:.1f}%)'
                    )
                else:
                    total_after += original_size * 0.3
                    self.stdout.write(f'  📋 Would optimize: {post.title} ({original_size/1024:.1f}KB)')
                
                count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error with {post.title}: {e}'))
        
        return total_before, total_after, count

    def _optimize_category_images(self, dry_run):
        """Optimize all category images"""
        total_before = 0
        total_after = 0
        count = 0
        
        categories = RoomCategory.objects.exclude(image='')
        
        for category in categories:
            if not category.image:
                continue
            
            try:
                image_path = category.image.path
                if not os.path.exists(image_path):
                    continue
                
                # Get original size
                original_size = os.path.getsize(image_path)
                total_before += original_size
                
                if not dry_run:
                    # Optimize the image
                    with open(image_path, 'rb') as f:
                        optimized = optimize_image(f, max_width=1200, max_height=1200, quality=85)
                        category.image.save(
                            os.path.basename(image_path),
                            File(optimized),
                            save=False
                        )
                        category.save()
                    
                    # Get new size
                    new_size = os.path.getsize(category.image.path)
                    total_after += new_size
                    savings = ((original_size - new_size) / original_size) * 100
                    
                    self.stdout.write(
                        f'  ✅ {category.name}: '
                        f'{original_size/1024:.1f}KB → {new_size/1024:.1f}KB '
                        f'(saved {savings:.1f}%)'
                    )
                else:
                    total_after += original_size * 0.3
                    self.stdout.write(f'  📋 Would optimize: {category.name} ({original_size/1024:.1f}KB)')
                
                count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error with {category.name}: {e}'))
        
        return total_before, total_after, count

