import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sofahub_backend.settings')
django.setup()

from products.models import Category, Tag, Product, ProductVariation


def create_categories():
    """Create hierarchical categories for furniture"""
    print("=== Creating Categories ===")

    categories_data = [
        # Main categories (no parent)
        {"name": "Living Room", "slug": "living-room", "parent": None},
        {"name": "Bedroom", "slug": "bedroom", "parent": None},
        {"name": "Dining", "slug": "dining", "parent": None},
        {"name": "Office", "slug": "office", "parent": None},
        {"name": "Outdoor", "slug": "outdoor", "parent": None},

        # Subcategories for Living Room
        {"name": "Sofas", "slug": "sofas", "parent": "Living Room"},
        {"name": "Chairs", "slug": "chairs", "parent": "Living Room"},
        {"name": "Coffee Tables", "slug": "coffee-tables", "parent": "Living Room"},
        {"name": "TV Stands", "slug": "tv-stands", "parent": "Living Room"},

        # Subcategories for Bedroom
        {"name": "Beds", "slug": "beds", "parent": "Bedroom"},
        {"name": "Wardrobes", "slug": "wardrobes", "parent": "Bedroom"},
        {"name": "Dressers", "slug": "dressers", "parent": "Bedroom"},

        # Subcategories for Dining
        {"name": "Dining Tables", "slug": "dining-tables", "parent": "Dining"},
        {"name": "Dining Chairs", "slug": "dining-chairs", "parent": "Dining"},

        # Sub-subcategories
        {"name": "3-Seater Sofas", "slug": "3-seater-sofas", "parent": "Sofas"},
        {"name": "2-Seater Sofas", "slug": "2-seater-sofas", "parent": "Sofas"},
        {"name": "King Size Beds", "slug": "king-size-beds", "parent": "Beds"},
        {"name": "Queen Size Beds", "slug": "queen-size-beds", "parent": "Beds"},
    ]

    created_categories = {}

    for cat_data in categories_data:
        parent = None
        if cat_data["parent"]:
            parent = created_categories.get(cat_data["parent"])

        category, created = Category.objects.get_or_create(
            name=cat_data["name"],
            defaults={
                'slug': cat_data["slug"],
                'parent': parent,
                'description': f"Beautiful {cat_data['name'].lower()} for your home",
                'is_active': True
            }
        )

        if created:
            print(f"✅ Created category: {cat_data['name']}")
        else:
            print(f"ℹ️ Category exists: {cat_data['name']}")

        created_categories[cat_data["name"]] = category

    return created_categories


def create_tags():
    """Create product tags"""
    print("\n=== Creating Tags ===")

    tags_data = [
        {"name": "On Sale", "slug": "on-sale", "color_code": "#FF0000"},
        {"name": "New Arrival", "slug": "new-arrival", "color_code": "#00FF00"},
        {"name": "Bestseller", "slug": "bestseller", "color_code": "#0000FF"},
        {"name": "Eco-Friendly", "slug": "eco-friendly", "color_code": "#008000"},
        {"name": "Luxury", "slug": "luxury", "color_code": "#FFD700"},
        {"name": "Modern", "slug": "modern", "color_code": "#800080"},
        {"name": "Customizable", "slug": "customizable", "color_code": "#FFA500"},
    ]

    created_tags = {}

    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_data["name"],
            defaults={
                'slug': tag_data["slug"],
                'color_code': tag_data["color_code"]
            }
        )

        if created:
            print(f"✅ Created tag: {tag_data['name']}")
        else:
            print(f"ℹ️ Tag exists: {tag_data['name']}")

        created_tags[tag_data["name"]] = tag

    return created_tags


def create_products(categories, tags):
    """Create sample furniture products with multiple category assignments"""
    print("\n=== Creating Products ===")

    products_data = [
        {
            "name": "Premium Leather Sofa",
            "slug": "premium-leather-sofa",
            "description": "Luxurious 3-seater leather sofa with premium craftsmanship and comfortable seating. Perfect for your living room.",
            "base_price": 85000.00,
            "sale_price": 75000.00,
            "categories": ["Living Room", "Sofas", "3-Seater Sofas"],
            "tags": ["Luxury", "On Sale", "Bestseller"],
            "variations": [
                {"color": "Black", "material": "Leather", "sku": "SOFA-BLK-LTH-001", "price_modifier": 0},
                {"color": "Brown", "material": "Leather", "sku": "SOFA-BRN-LTH-001", "price_modifier": 5000},
                {"color": "Cream", "material": "Leather", "sku": "SOFA-CRM-LTH-001", "price_modifier": 3000},
            ]
        },
        {
            "name": "Modern Fabric Sectional",
            "slug": "modern-fabric-sectional",
            "description": "Contemporary L-shaped sectional sofa with soft fabric upholstery. Great for family gatherings.",
            "base_price": 65000.00,
            "sale_price": None,
            "categories": ["Living Room", "Sofas"],
            "tags": ["Modern", "New Arrival"],
            "variations": [
                {"color": "Gray", "material": "Fabric", "sku": "SECTIONAL-GRY-FAB-001", "price_modifier": 0},
                {"color": "Navy Blue", "material": "Fabric", "sku": "SECTIONAL-NAV-FAB-001", "price_modifier": 2000},
            ]
        },
        {
            "name": "Dining Chair Set (4 pieces)",
            "slug": "dining-chair-set",
            "description": "Set of 4 elegant dining chairs with comfortable padding and sturdy construction.",
            "base_price": 35000.00,
            "sale_price": 29900.00,
            "categories": ["Dining", "Dining Chairs", "Chairs"],
            "tags": ["Modern", "On Sale"],
            "variations": [
                {"color": "Black", "material": "Wood", "sku": "CHAIR-DINING-BLK-001", "price_modifier": 0},
                {"color": "White", "material": "Wood", "sku": "CHAIR-DINING-WHT-001", "price_modifier": 2000},
                {"color": "Walnut", "material": "Wood", "sku": "CHAIR-DINING-WAL-001", "price_modifier": 3000},
            ]
        },
        {
            "name": "King Size Storage Bed",
            "slug": "king-size-storage-bed",
            "description": "Elegant king size bed with built-in storage drawers and comfortable headboard.",
            "base_price": 45000.00,
            "sale_price": 39900.00,
            "categories": ["Bedroom", "Beds", "King Size Beds"],
            "tags": ["Bestseller", "On Sale", "Modern"],
            "variations": [
                {"color": "Dark Oak", "material": "Wood", "sku": "BED-KING-OAK-001", "price_modifier": 0},
                {"color": "White", "material": "Wood", "sku": "BED-KING-WHT-001", "price_modifier": -2000},
                {"color": "Walnut", "material": "Wood", "sku": "BED-KING-WAL-001", "price_modifier": 3000},
            ]
        },
        {
            "name": "Office Executive Chair",
            "slug": "office-executive-chair",
            "description": "Ergonomic executive chair with lumbar support and adjustable height. Perfect for long work hours.",
            "base_price": 25000.00,
            "sale_price": 22000.00,
            "categories": ["Office", "Chairs"],
            "tags": ["Eco-Friendly", "On Sale", "Modern"],
            "variations": [
                {"color": "Black", "material": "Mesh", "sku": "CHAIR-OFFICE-BLK-001", "price_modifier": 0},
                {"color": "Gray", "material": "Mesh", "sku": "CHAIR-OFFICE-GRY-001", "price_modifier": 0},
            ]
        },
        {
            "name": "Convertible Sofa Bed",
            "slug": "convertible-sofa-bed",
            "description": "Multi-functional sofa that converts into a comfortable bed. Perfect for small spaces.",
            "base_price": 55000.00,
            "sale_price": 49000.00,
            "categories": ["Living Room", "Bedroom", "Sofas", "Beds"],
            "tags": ["Modern", "On Sale", "Customizable"],
            "variations": [
                {"color": "Beige", "material": "Fabric", "sku": "SOFABED-BEIGE-001", "price_modifier": 0},
                {"color": "Charcoal", "material": "Fabric", "sku": "SOFABED-CHAR-001", "price_modifier": 3000},
            ]
        },
        {
            "name": "Accent Armchair",
            "slug": "accent-armchair",
            "description": "Comfortable accent armchair perfect for living room corners or bedroom reading nooks.",
            "base_price": 18000.00,
            "sale_price": 15000.00,
            "categories": ["Living Room", "Bedroom", "Chairs"],
            "tags": ["Modern", "On Sale"],
            "variations": [
                {"color": "Gray", "material": "Fabric", "sku": "CHAIR-ACCENT-GRY-001", "price_modifier": 0},
                {"color": "Navy Blue", "material": "Fabric", "sku": "CHAIR-ACCENT-NAV-001", "price_modifier": 1500},
            ]
        },
        {
            "name": "Coffee Table with Storage",
            "slug": "coffee-table-storage",
            "description": "Modern coffee table with hidden storage compartment. Functional and stylish.",
            "base_price": 15000.00,
            "sale_price": 12900.00,
            "categories": ["Living Room", "Coffee Tables"],
            "tags": ["Modern", "On Sale", "Eco-Friendly"],
            "variations": [
                {"color": "Oak", "material": "Wood", "sku": "TABLE-COFFEE-OAK-001", "price_modifier": 0},
                {"color": "Black", "material": "Glass/Wood", "sku": "TABLE-COFFEE-BLK-001", "price_modifier": 2000},
            ]
        }
    ]

    created_products = {}

    for product_data in products_data:
        sale_start = datetime.now() - timedelta(days=1) if product_data["sale_price"] else None
        sale_end = datetime.now() + timedelta(days=30) if product_data["sale_price"] else None

        product, created = Product.objects.get_or_create(
            name=product_data["name"],
            defaults={
                'slug': product_data["slug"],
                'description': product_data["description"],
                'base_price': product_data["base_price"],
                'sale_price': product_data["sale_price"],
                'sale_start': sale_start,
                'sale_end': sale_end,
                'is_active': True
            }
        )

        if created:
            # Add MULTIPLE categories
            for cat_name in product_data["categories"]:
                category = categories.get(cat_name)
                if category:
                    product.categories.add(category)

            # Add tags
            for tag_name in product_data["tags"]:
                tag = tags.get(tag_name)
                if tag:
                    product.tags.add(tag)

            # Create variations
            for variation_data in product_data["variations"]:
                ProductVariation.objects.create(
                    product=product,
                    sku=variation_data["sku"],
                    attributes=variation_data,
                    stock_quantity=random.randint(2, 10),
                    price_modifier=variation_data["price_modifier"],
                    is_active=True
                )

            category_names = ", ".join(product_data["categories"])
            tag_names = ", ".join(product_data["tags"])
            print(f"✅ Created: {product_data['name']}")
            print(f"   Categories: {category_names}")
            print(f"   Tags: {tag_names}")
            print(f"   Variations: {len(product_data['variations'])}")
            print()
        else:
            print(f"ℹ️ Product exists: {product_data['name']}")

        created_products[product_data["name"]] = product

    return created_products


def main():
    print("🛋️ SOFA HUB Test Data Creation")
    print("=" * 60)

    # Create all test data
    categories = create_categories()
    tags = create_tags()
    products = create_products(categories, tags)

    # Summary
    print("=" * 60)
    print("📊 TEST DATA SUMMARY:")
    print(f"📁 Categories: {len(categories)}")
    print(f"🏷️ Tags: {len(tags)}")
    print(f"🛋️ Products: {len(products)}")

    # Count variations
    total_variations = ProductVariation.objects.count()
    print(f"🎨 Product Variations: {total_variations}")
    print("=" * 60)
    print("✅ Test data creation completed successfully!")
    print("🚀 Run the next script to test API endpoints: python 2_test_api.py")


if __name__ == "__main__":
    main()