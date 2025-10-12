# Frontend Image Gallery API Guide

## Overview
The backend now provides comprehensive image data for product galleries/carousels. All images are properly ordered and include navigation metadata.

## API Endpoints

### 1. Product Detail (includes all images)
```
GET /api/products/{slug}/
```

**Response includes:**
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
      "order": 0,
      "index": 0,
      "is_first": true,
      "is_last": false,
      "total_count": 3
    },
    {
      "id": 2,
      "image": "https://sofahubbackend-production.up.railway.app/api/images/2/",
      "alt_text": "Side view",
      "is_primary": false,
      "order": 1,
      "index": 1,
      "is_first": false,
      "is_last": false,
      "total_count": 3
    },
    {
      "id": 3,
      "image": "https://sofahubbackend-production.up.railway.app/api/images/3/",
      "alt_text": "Detail view",
      "is_primary": false,
      "order": 2,
      "index": 2,
      "is_first": false,
      "is_last": true,
      "total_count": 3
    }
  ]
}
```

### 2. Dedicated Images Endpoint
```
GET /api/products/{slug}/images/
```

**Response:**
```json
{
  "product_id": 1,
  "product_name": "Sofa Set",
  "total_images": 3,
  "images": [
    // Same structure as above
  ]
}
```

## Image Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique image ID |
| `image` | string | Full URL to image |
| `alt_text` | string | Alt text for accessibility |
| `is_primary` | boolean | Is this the main product image? |
| `order` | integer | Display order (0 = first) |
| `index` | integer | Current position in array (0-based) |
| `is_first` | boolean | Is this the first image? |
| `is_last` | boolean | Is this the last image? |
| `total_count` | integer | Total number of images |

## Frontend Implementation Examples

### JavaScript/React Gallery
```javascript
// Get product data
const response = await fetch(`/api/products/${productSlug}/`);
const product = await response.json();

// Gallery state
const [currentImageIndex, setCurrentImageIndex] = useState(0);
const images = product.images;

// Navigation functions
const nextImage = () => {
  if (currentImageIndex < images.length - 1) {
    setCurrentImageIndex(currentImageIndex + 1);
  }
};

const prevImage = () => {
  if (currentImageIndex > 0) {
    setCurrentImageIndex(currentImageIndex - 1);
  }
};

// Render gallery
return (
  <div className="image-gallery">
    <img 
      src={images[currentImageIndex].image} 
      alt={images[currentImageIndex].alt_text}
    />
    
    {images.length > 1 && (
      <>
        <button 
          onClick={prevImage}
          disabled={images[currentImageIndex].is_first}
        >
          Previous
        </button>
        
        <button 
          onClick={nextImage}
          disabled={images[currentImageIndex].is_last}
        >
          Next
        </button>
        
        <div className="image-counter">
          {currentImageIndex + 1} / {images[currentImageIndex].total_count}
        </div>
      </>
    )}
  </div>
);
```

### Thumbnail Navigation
```javascript
return (
  <div className="gallery">
    {/* Main image */}
    <div className="main-image">
      <img src={images[currentImageIndex].image} alt={images[currentImageIndex].alt_text} />
    </div>
    
    {/* Thumbnails */}
    <div className="thumbnails">
      {images.map((image, index) => (
        <img
          key={image.id}
          src={image.image}
          alt={image.alt_text}
          className={index === currentImageIndex ? 'active' : ''}
          onClick={() => setCurrentImageIndex(index)}
        />
      ))}
    </div>
  </div>
);
```

## Key Features

### ✅ All Images Included
- The API now returns ALL images for a product
- Images are properly ordered by the `order` field
- No more missing images in galleries

### ✅ Navigation Metadata
- `is_first` and `is_last` help with button states
- `index` and `total_count` for counters
- `is_primary` to highlight the main image

### ✅ Proper Ordering
- Images are ordered by `order` field (0 = first)
- Secondary sort by `id` for consistency
- Frontend receives images in correct display order

### ✅ Reliable URLs
- All image URLs use ID-based serving
- Graceful fallback if files are missing
- Consistent URL format: `/api/images/{id}/`

## Migration from Old System

### Before (Only Primary Image)
```javascript
// Old way - only showed primary image
const primaryImage = product.images.find(img => img.is_primary);
<img src={primaryImage?.image} alt={primaryImage?.alt_text} />
```

### After (Full Gallery)
```javascript
// New way - show all images with navigation
{product.images.map((image, index) => (
  <img 
    key={image.id}
    src={image.image} 
    alt={image.alt_text}
    className={index === currentIndex ? 'active' : ''}
  />
))}
```

## Testing

Test these URLs to verify the API:
- `https://sofahubbackend-production.up.railway.app/api/products/test-product/`
- `https://sofahubbackend-production.up.railway.app/api/products/test-product/images/`

Both should return all images with proper metadata.

## Error Handling

The image URLs (`/api/images/{id}/`) are bulletproof:
- Returns the image if file exists
- Returns a fallback image if file is missing
- Never returns 404 (always serves something)

This ensures your frontend never breaks due to missing image files.
