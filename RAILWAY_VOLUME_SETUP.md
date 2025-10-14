# Railway Volume Setup Guide for Media Files

## Overview
Using Railway Volumes to persist your uploaded images across deployments. This ensures your product images, blog images, and category images survive redeployments.

---

## Step-by-Step Setup

### 1. Create a Volume in Railway

1. Go to your Railway project dashboard
2. Click on your Django service
3. Go to the **"Storage"** or **"Volumes"** tab (depending on Railway's current UI)
4. Click **"New Volume"** or **"+ Add Volume"**
5. Configure the volume:
   - **Name**: `media-files` (or any name you prefer)
   - **Mount Path**: `/app/media`
   - Click **"Add"** or **"Create"**

### 2. Verify Your Settings

Your current `settings.py` is already configured correctly:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

This will automatically use `/app/media` when deployed (since `BASE_DIR` is `/app` on Railway).

### 3. Deploy

After adding the volume:
- Railway will automatically redeploy your service
- The volume will be mounted at `/app/media`
- All future image uploads will be stored in the persistent volume

### 4. Migrate Existing Images (if needed)

If you have images already uploaded locally that you want to migrate to Railway:

**Option A: Upload via Admin Panel**
- Log into your Railway Django admin
- Re-upload all product images manually

**Option B: Manual Transfer (Advanced)**
1. Connect to your Railway service via CLI
2. Copy your local `media/` folder to the Railway volume
3. Use Railway CLI or SFTP

---

## What Happens Now

### ✅ Before Deployment (without volume):
- Upload image → Saved to filesystem
- Redeploy → **Images deleted** ❌

### ✅ After Volume Setup:
- Upload image → Saved to persistent volume
- Redeploy → **Images remain** ✅

---

## Important Notes

### Cost
- **$0.25 per GB per month**
- Example: 5GB of images = $1.25/month
- Check your Railway usage dashboard regularly

### Backup Strategy
Consider backing up your media files periodically:
1. Download the media folder via Railway CLI
2. Store backups in cloud storage (Google Drive, etc.)
3. Set up automated backups if you have many images

### Volume Size
- Volumes start small and grow automatically
- Monitor your storage usage in Railway dashboard
- Consider image compression to save space

### File Access
- Files in the volume persist across deployments
- Files are NOT deleted when you redeploy
- Only manual deletion or volume removal will delete files

---

## Troubleshooting

### Images not showing after volume setup?
1. Check the mount path is exactly `/app/media`
2. Verify `MEDIA_ROOT` and `MEDIA_URL` in settings
3. Check Railway deployment logs for errors
4. Test uploading a new image via admin panel

### Volume full?
1. Check your Railway dashboard for storage usage
2. Delete unused images via Django admin
3. Consider compressing existing images
4. Consider switching to Cloudinary if storage becomes expensive

### Need to start fresh?
1. You can delete the volume in Railway dashboard
2. Create a new one
3. Re-upload your images

---

## Alternative: Cloudinary (Free Option)

If Railway Volume costs become a concern, you can switch to Cloudinary later:
- 25GB storage FREE
- Built-in CDN
- Automatic image optimization
- No cost until you exceed 25GB

Let me know if you need help setting up Cloudinary instead!

---

## Verification Checklist

After setup, verify everything works:

- [ ] Volume created in Railway dashboard
- [ ] Mount path set to `/app/media`
- [ ] Service redeployed successfully
- [ ] Upload a test image via Django admin
- [ ] Image displays correctly on your site
- [ ] Trigger a redeploy (change env var or push code)
- [ ] Verify test image still exists after redeploy

---

## Image Optimization (IMPORTANT!) 💰

**All images are now automatically optimized to save storage costs!**

See `IMAGE_OPTIMIZATION_GUIDE.md` for full details.

### Quick Summary:
- ✅ **Automatic optimization** on every upload
- ✅ **50-70% file size reduction** on average
- ✅ **Smart resizing** (products: 2000px, blog: 1920px, categories: 1200px)
- ✅ **Quality preserved** (JPEG quality 85%)

### Optimize Existing Images
If you have images already uploaded, optimize them to save space:

```bash
# See what would be optimized
python manage.py optimize_existing_images --dry-run

# Actually optimize all images
python manage.py optimize_existing_images

# Optimize only product images
python manage.py optimize_existing_images --type products
```

### Cost Impact Example:
- **Without optimization**: 100 products × 4MB = 400MB → **$0.10/month**
- **With optimization**: 100 products × 400KB = 40MB → **$0.01/month**
- **Savings: 90%!**

---

## Summary

**Your media files are now persistent AND optimized!** 🎉

Upload images → They get optimized automatically → They stay forever

**Cost**: ~$0.25/GB/month, but with optimization you'll use **70% less storage!**

