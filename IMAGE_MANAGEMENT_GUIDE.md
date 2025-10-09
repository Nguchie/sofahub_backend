# Image Management Guide

## Overview
This system provides robust, production-ready image handling for your eCommerce platform.

## Key Features

### 🔐 Automatic UUID Filenames
- All uploaded images get unique UUID-based filenames
- Prevents filename conflicts and overwrites
- Example: `091032affbe1437586b0dc92800f7bbf.jpg`

### 🧹 Automatic Cleanup
- When you delete an image in admin, the file is automatically removed from the filesystem
- When you replace an image, the old file is automatically deleted
- No orphaned files cluttering your storage

### 🔄 Graceful Fallback
- If an image file is missing, the system serves a fallback image
- Frontend never breaks due to missing images
- Admin panel shows file status (green checkmark = OK, red X = missing)

### 🛡️ ID-Based Serving
- Images are served via `/api/images/{id}/` URLs
- More reliable than direct file paths
- Handles missing files gracefully

## How to Use

### Adding Product Images (Admin Panel)

1. **Go to Products > Products**
2. **Click on a product** or create a new one
3. **Scroll to "Product Images" section**
4. **Click "Add another Product image"**
5. **Choose file** and fill in:
   - Image: Select your image file
   - Alt text: Description for accessibility
   - Is primary: Check if this is the main product image
   - Order: Number for sorting (0 = first)
6. **Click "Save"**

### Updating Images

1. **Find the product** in admin
2. **Locate the image** you want to update
3. **Click "Change:"** next to the current image
4. **Select new file**
5. **Click "Save"**
   - Old image file is automatically deleted ✨
   - New image gets a unique filename ✨

### Deleting Images

1. **Find the product** in admin
2. **Check "DELETE"** box next to the image
3. **Click "Save"**
   - Image file is automatically removed from filesystem ✨

### Checking Image Health

The admin panel shows:
- **Green checkmark (✓)**: Image file exists, with file size
- **Red X (✗)**: Image file is missing
- **Preview**: Live preview of the image

## Management Commands

### Verify System Health
```bash
python manage.py verify_images
```
Shows:
- How many products have images
- How many image records are working
- Overall health score

### Clean Up Orphaned Data
```bash
python manage.py cleanup_images
```
- Removes database records for missing files
- Lists files without database records

### Run on Deployment
These commands run automatically on Railway deployment:
- `cleanup_images` - Removes orphaned records
- `verify_images` - Checks system health

## API Endpoints

### Get Product Details
```
GET /api/products/{slug}/
```
Returns product with all images:
```json
{
  "id": 1,
  "name": "Sofa Set",
  "images": [
    {
      "id": 1,
      "image": "https://sofahubbackend-production.up.railway.app/api/images/1/",
      "alt_text": "Front view",
      "is_primary": true,
      "order": 0
    }
  ]
}
```

### Serve Image by ID
```
GET /api/images/{id}/
```
- Serves the image file
- Returns 200 with image data (success)
- Returns 404 if image doesn't exist
- Automatically uses fallback if file is missing

## Best Practices

### ✅ DO:
- Upload images through Django admin
- Let the system generate UUID filenames
- Check the green checkmark to verify uploads
- Use `is_primary` to mark main product images
- Use `order` field to control image sequence

### ❌ DON'T:
- Manually upload files to `/media/products/` folder
- Rename files in the filesystem
- Delete files directly from filesystem
- Use the same filename for multiple products

## Troubleshooting

### Images Not Loading on Frontend?

1. **Check admin panel** - Does the image have a green checkmark?
2. **Run verify command**:
   ```bash
   python manage.py verify_images
   ```
3. **Check the logs** - Look for errors in Railway logs
4. **Test the URL directly** - Visit `/api/images/{id}/` in browser

### "File Missing" in Admin?

1. **Run cleanup**:
   ```bash
   python manage.py cleanup_images
   ```
2. **Re-upload the image** in admin panel

### Orphaned Files?

Run:
```bash
python manage.py cleanup_images
```
It will list files that have no database records.

## Technical Details

### Storage
- **Local Development**: Files stored in `/media/products/`
- **Production (Railway)**: Files stored in persistent volume mounted at `/app/media/`

### File Handling
- **Upload**: UUID generated → File saved → DB record created
- **Update**: New file saved → Old file deleted → DB updated
- **Delete**: DB record deleted → File automatically removed (via signals)

### Signals
- `post_delete`: Cleans up file when ProductImage is deleted
- `pre_save`: Cleans up old file when image is replaced

## Production Deployment

Railway automatically:
1. Runs migrations
2. Cleans up orphaned images
3. Verifies system health
4. Collects static files
5. Starts Gunicorn

All image operations are logged for debugging.

## Support

If you encounter issues:
1. Check Railway logs
2. Run `verify_images` command
3. Check admin panel status indicators
4. Verify database and filesystem are in sync

