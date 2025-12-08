# Product Type Filtering by Room Category - API Usage

## Overview
The product type filter is now context-aware based on the room category. When viewing a specific room category page, only relevant product types will be shown.

## API Endpoints

### 1. Get All Product Types (No Filter)
```
GET /api/products/product-types/
```
**Returns:** All active product types

**Example Response:**
```json
[
  { "id": 1, "name": "Sofa", "slug": "sofa", "product_count": 15 },
  { "id": 2, "name": "Bed", "slug": "bed", "product_count": 10 },
  { "id": 3, "name": "2-Seater Dining Set", "slug": "2-seater-dining-set", "product_count": 5 },
  { "id": 4, "name": "4-Seater Dining Set", "slug": "4-seater-dining-set", "product_count": 3 }
]
```

---

### 2. Get Product Types for Specific Room Category (Filtered)
```
GET /api/products/product-types/?room_category=living-room
```
**Returns:** Only product types that have products in the "Living Room" category

**Example Response:**
```json
[
  { "id": 1, "name": "Sofa", "slug": "sofa", "product_count": 12 },
  { "id": 2, "name": "Bed", "slug": "bed", "product_count": 8 }
]
```
*Note: Dining sets are excluded because they don't belong to Living Room*

---

### 3. Get Product Types for Dining Room
```
GET /api/products/product-types/?room_category=dining-room
```
**Returns:** Only product types that have products in the "Dining Room" category

**Example Response:**
```json
[
  { "id": 3, "name": "2-Seater Dining Set", "slug": "2-seater-dining-set", "product_count": 5 },
  { "id": 4, "name": "4-Seater Dining Set", "slug": "4-seater-dining-set", "product_count": 3 }
]
```
*Note: Sofas and beds are excluded because they don't belong to Dining Room*

---

## Frontend Implementation

### Example: Living Room Page

```javascript
// 1. Detect current room category from URL or state
const roomCategory = 'living-room'; // from URL: /living-room

// 2. Fetch available product types for this room
const response = await fetch(
  `/api/products/product-types/?room_category=${roomCategory}`
);
const productTypes = await response.json();

// 3. Render product type filter with only relevant options
// productTypes will only contain: Sofas, Beds, Armchairs, etc.
// (no dining sets or office furniture)

// 4. When user selects a product type filter, fetch products
const selectedType = 'sofa';
const productsResponse = await fetch(
  `/api/products/?room_category=${roomCategory}&product_type=${selectedType}`
);
const products = await productsResponse.json();
```

### Example: Dining Room Page

```javascript
// 1. Detect current room category
const roomCategory = 'dining-room'; // from URL: /dining-room

// 2. Fetch available product types for this room
const response = await fetch(
  `/api/products/product-types/?room_category=${roomCategory}`
);
const productTypes = await response.json();

// 3. Render product type filter with only relevant options
// productTypes will only contain: 2-Seater Dining Set, 4-Seater Dining Set, etc.
// (no sofas or beds)

// 4. When user applies filters
const selectedType = '4-seater-dining-set';
const productsResponse = await fetch(
  `/api/products/?room_category=${roomCategory}&product_type=${selectedType}`
);
const products = await productsResponse.json();
```

### Example: All Products Page (No Room Filter)

```javascript
// 1. No room category specified
const roomCategory = null;

// 2. Fetch ALL product types
const response = await fetch('/api/products/product-types/');
const productTypes = await response.json();

// 3. Render product type filter with ALL options
// productTypes will contain: Sofas, Beds, Dining Sets, Office Chairs, etc.

// 4. When user selects a product type filter
const selectedType = 'sofa';
const productsResponse = await fetch(
  `/api/products/?product_type=${selectedType}`
);
const products = await productsResponse.json();
```

---

## React Example

```jsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function ProductListPage() {
  const { roomSlug } = useParams(); // e.g., "living-room" from URL
  const [productTypes, setProductTypes] = useState([]);
  const [selectedType, setSelectedType] = useState('');
  const [products, setProducts] = useState([]);

  // Fetch product types when room category changes
  useEffect(() => {
    const fetchProductTypes = async () => {
      const url = roomSlug 
        ? `/api/products/product-types/?room_category=${roomSlug}`
        : '/api/products/product-types/';
      
      const response = await fetch(url);
      const data = await response.json();
      setProductTypes(data);
    };

    fetchProductTypes();
  }, [roomSlug]);

  // Fetch products when filters change
  useEffect(() => {
    const fetchProducts = async () => {
      let url = '/api/products/?';
      
      if (roomSlug) url += `room_category=${roomSlug}&`;
      if (selectedType) url += `product_type=${selectedType}&`;
      
      const response = await fetch(url);
      const data = await response.json();
      setProducts(data.results);
    };

    fetchProducts();
  }, [roomSlug, selectedType]);

  return (
    <div>
      <h1>{roomSlug ? roomSlug.replace('-', ' ') : 'All Products'}</h1>
      
      {/* Product Type Filter */}
      <select 
        value={selectedType} 
        onChange={(e) => setSelectedType(e.target.value)}
      >
        <option value="">All Types</option>
        {productTypes.map(type => (
          <option key={type.id} value={type.slug}>
            {type.name} ({type.product_count})
          </option>
        ))}
      </select>

      {/* Product List */}
      <div>
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}
```

---

## Key Features

1. **Dynamic Filtering**: Product types are filtered based on the room category
2. **Context-Aware Counts**: The `product_count` shows only products in the filtered category
3. **Backwards Compatible**: If no `room_category` is specified, all product types are returned
4. **Efficient Queries**: Uses Django's `distinct()` to avoid duplicate results
5. **Only Active Products**: Only shows product types that have active products

---

## Testing the API

### Test 1: Get all product types
```bash
curl http://localhost:8000/api/products/product-types/
```

### Test 2: Get product types for Living Room
```bash
curl http://localhost:8000/api/products/product-types/?room_category=living-room
```

### Test 3: Get product types for Dining Room
```bash
curl http://localhost:8000/api/products/product-types/?room_category=dining-room
```

### Test 4: Get products with both filters
```bash
curl "http://localhost:8000/api/products/?room_category=living-room&product_type=sofa"
```

