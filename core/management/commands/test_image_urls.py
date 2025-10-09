from django.core.management.base import BaseCommand
from products.models import ProductImage
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Test image URLs to see if they work'

    def handle(self, *args, **options):
        self.stdout.write("🧪 TESTING IMAGE URLS")
        self.stdout.write("=" * 50)
        
        # Test the image URLs directly
        base_url = "https://sofahubbackend-production.up.railway.app"
        
        images = ProductImage.objects.all()
        
        for image in images:
            self.stdout.write(f"\n🖼️  Testing Image ID: {image.id}")
            self.stdout.write(f"   DB filename: {image.image.name}")
            
            # Test ID-based URL
            id_url = f"{base_url}/api/images/{image.id}/"
            self.stdout.write(f"   ID URL: {id_url}")
            
            try:
                response = requests.get(id_url, timeout=10)
                self.stdout.write(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    self.stdout.write(f"   ✅ Image served successfully ({len(response.content)} bytes)")
                    self.stdout.write(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                else:
                    self.stdout.write(f"   ❌ Failed to serve image")
                    
            except requests.exceptions.RequestException as e:
                self.stdout.write(f"   ❌ Request failed: {str(e)}")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("✅ URL testing completed!")
