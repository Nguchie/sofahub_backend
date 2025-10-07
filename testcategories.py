def create_products(self):
    """Create sample furniture products with multiple category assignments"""
    print("\n=== Creating Products ===")

    products_data = [
        {
            "name": "Premium Leather Sofa",
            "slug": "premium-leather-sofa",
            "description": "Luxurious 3-seater leather sofa with premium craftsmanship.",
            "base_price": 85000.00,
            "sale_price": 75000.00,
            "categories": ["Living Room", "Sofas", "3-Seater Sofas"],  # Multiple categories!
            "tags": ["Luxury", "On Sale"],
            "variations": [
                {"color": "Black", "material": "Leather", "sku": "SOFA-BLK-LTH-001", "price_modifier": 0},
                {"color": "Brown", "material": "Leather", "sku": "SOFA-BRN-LTH-001", "price_modifier": 5000},
            ]
        },
        {
            "name": "Dining Chair Set",
            "slug": "dining-chair-set",
            "description": "Set of 4 elegant dining chairs with comfortable padding.",
            "base_price": 35000.00,
            "sale_price": 29900.00,
            "categories": ["Dining", "Chairs"],  # Belongs to both Dining and Chairs
            "tags": ["Modern", "On Sale"],
            "variations": [
                {"color": "Black", "material": "Wood", "sku": "CHAIR-DINING-BLK-001", "price_modifier": 0},
                {"color": "White", "material": "Wood", "sku": "CHAIR-DINING-WHT-001", "price_modifier": 2000},
            ]
        },
        {
            "name": "Accent Armchair",
            "slug": "accent-armchair",
            "description": "Comfortable accent armchair for living room or bedroom.",
            "base_price": 25000.00,
            "sale_price": None,
            "categories": ["Living Room", "Bedroom", "Chairs"],  # Multiple categories!
            "tags": ["Modern", "Bestseller"],
            "variations": [
                {"color": "Gray", "material": "Fabric", "sku": "CHAIR-ACCENT-GRY-001", "price_modifier": 0},
                {"color": "Navy Blue", "material": "Fabric", "sku": "CHAIR-ACCENT-NAV-001", "price_modifier": 1500},
            ]
        },
        {
            "name": "Office Executive Chair",
            "slug": "office-executive-chair",
            "description": "Ergonomic executive chair for office use.",
            "base_price": 28000.00,
            "sale_price": 25000.00,
            "categories": ["Office", "Chairs"],  # Office category + Chairs
            "tags": ["Eco-Friendly", "On Sale"],
            "variations": [
                {"color": "Black", "material": "Mesh", "sku": "CHAIR-OFFICE-BLK-001", "price_modifier": 0},
                {"color": "Gray", "material": "Mesh", "sku": "CHAIR-OFFICE-GRY-001", "price_modifier": 0},
            ]
        },
        {
            "name": "Convertible Sofa Bed",
            "slug": "convertible-sofa-bed",
            "description": "Multi-functional sofa that converts into a comfortable bed.",
            "base_price": 55000.00,
            "sale_price": 49000.00,
            "categories": ["Living Room", "Bedroom", "Sofas", "Beds"],  # Multiple categories!
            "tags": ["Modern", "On Sale", "Bestseller"],
            "variations": [
                {"color": "Beige", "material": "Fabric", "sku": "SOFABED-BEIGE-001", "price_modifier": 0},
                {"color": "Charcoal", "material": "Fabric", "sku": "SOFABED-CHAR-001", "price_modifier": 3000},
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
            # Add MULTIPLE categories using ManyToMany
            for cat_name in product_data["categories"]:
                category = self.created_data['categories'].get(cat_name)
                if category:
                    product.categories.add(category)  # This adds to ManyToMany relationship

            # Add tags
            for tag_name in product_data["tags"]:
                tag = self.created_data['tags'].get(tag_name)
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
            print(f"✅ Created product: {product_data['name']}")
            print(f"   Categories: {category_names}")
            print(f"   Variations: {len(product_data['variations'])}")
        else:
            print(f"ℹ️ Product exists: {product_data['name']}")

        created_products[product_data["name"]] = product

    self.created_data['products'] = created_products
    return created_products