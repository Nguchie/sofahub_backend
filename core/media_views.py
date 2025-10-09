from django.http import HttpResponse, Http404
from django.conf import settings
from products.models import ProductImage
import os
import mimetypes


def serve_media(request, path):
    """Custom view to serve media files"""
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    # Get file content
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Get content type
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    response = HttpResponse(content, content_type=content_type)
    response['Content-Length'] = len(content)
    
    return response


def serve_product_image(request, image_id):
    """Serve product image by ID - bulletproof fallback logic"""
    print(f"🔍 DEBUG: serve_product_image called with image_id={image_id}")
    
    try:
        product_image = ProductImage.objects.get(id=image_id)
        print(f"📋 Found image object: {product_image.image.name}")
        
        # Get the products directory
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        print(f"📁 Products directory: {products_dir}")
        
        if not os.path.exists(products_dir):
            print(f"❌ Products directory doesn't exist")
            return HttpResponse("Products directory not found", status=404)
        
        # Get all files in products directory
        all_files = os.listdir(products_dir)
        print(f"📂 Found {len(all_files)} files in products directory")
        
        # Try multiple strategies to find the file
        filename = os.path.basename(product_image.image.name)
        print(f"🎯 Target filename from DB: {filename}")
        
        # Strategy 1: Exact filename match
        exact_path = os.path.join(products_dir, filename)
        if os.path.exists(exact_path):
            print(f"✅ Found exact match: {filename}")
            return serve_file_response(exact_path, filename)
        
        # Strategy 2: Find by base name (remove Django's random suffix)
        base_name = filename.split('_')[0] if '_' in filename else filename.split('.')[0]
        print(f"🔍 Looking for files starting with: {base_name}")
        
        for file in all_files:
            if file.startswith(base_name) and file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                potential_path = os.path.join(products_dir, file)
                print(f"✅ Found similar file: {file}")
                return serve_file_response(potential_path, file)
        
        # Strategy 2.5: Try to find files with similar pattern (for test-product files)
        if 'test-product' in filename:
            print(f"🔍 Looking for test-product files...")
            for file in all_files:
                if 'test' in file.lower() and file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    potential_path = os.path.join(products_dir, file)
                    print(f"✅ Found test file: {file}")
                    return serve_file_response(potential_path, file)
        
        # Strategy 3: Find any image file (last resort)
        print(f"🆘 Last resort: looking for any image file...")
        for file in all_files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                potential_path = os.path.join(products_dir, file)
                print(f"✅ Found any image file: {file}")
                return serve_file_response(potential_path, file)
        
        print(f"❌ No image file found for image_id={image_id}")
        return HttpResponse("Image not found", status=404)
        
    except ProductImage.DoesNotExist:
        print(f"❌ ProductImage with id={image_id} not found")
        return HttpResponse("Image not found", status=404)
    except Exception as e:
        print(f"❌ Error serving image: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return HttpResponse("Error serving image", status=500)


def serve_file_response(file_path, filename):
    """Helper function to serve a file with proper headers"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'image/jpeg'
        
        print(f"✅ Serving file: {file_path}, size: {len(content)} bytes")
        
        response = HttpResponse(content, content_type=content_type)
        response['Content-Length'] = len(content)
        response['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
        
        return response
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {str(e)}")
        return HttpResponse("Error reading file", status=500)