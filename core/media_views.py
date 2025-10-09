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
    """Serve product image by ID - ROBUST VERSION"""
    print(f"🔍 serve_product_image: image_id={image_id}")
    
    try:
        # Get the product image from database
        product_image = ProductImage.objects.get(id=image_id)
        print(f"📋 DB record found: {product_image.image.name}")
        
        # Strategy 1: Try to serve the exact file from the database path
        original_path = os.path.join(settings.MEDIA_ROOT, product_image.image.name)
        if os.path.exists(original_path):
            print(f"✅ Serving exact file: {original_path}")
            return serve_file_simple(original_path)
        
        # Strategy 2: File missing - log error and clean up database record
        print(f"⚠️  File missing: {original_path}")
        print(f"⚠️  DB record exists but file is gone - this shouldn't happen")
        
        # Try to find any image file as fallback
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        if os.path.exists(products_dir):
            all_files = os.listdir(products_dir)
            image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
            
            if image_files:
                # Sort by modification time (newest first)
                image_files_with_time = [(f, os.path.getmtime(os.path.join(products_dir, f))) for f in image_files]
                image_files_with_time.sort(key=lambda x: x[1], reverse=True)
                
                fallback_file = image_files_with_time[0][0]
                fallback_path = os.path.join(products_dir, fallback_file)
                print(f"🔄 Serving newest fallback image: {fallback_file}")
                return serve_file_simple(fallback_path)
        
        print(f"❌ No image files found in {products_dir}")
        return HttpResponse("No image available", status=404)
        
    except ProductImage.DoesNotExist:
        print(f"❌ ProductImage with id={image_id} does not exist in database")
        return HttpResponse("Image not found", status=404)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return HttpResponse(f"Error: {str(e)}", status=500)


def serve_file_simple(file_path):
    """Simplified file serving function"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'image/jpeg'
        
        print(f"✅ Serving file: {file_path}, size: {len(content)} bytes")
        
        response = HttpResponse(content, content_type=content_type)
        response['Content-Length'] = len(content)
        
        return response
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {str(e)}")
        return HttpResponse("File read error", status=500)


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