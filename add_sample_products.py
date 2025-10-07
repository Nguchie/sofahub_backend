import os
import django
import random
from datetime import datetime, timedelta
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sofahub_backend.settings')
django.setup()

from products.models import RoomCategory, ProductType, Tag, Product, ProductVariation
from django.utils import timezone

class SampleProductCreator:
    def __init__(self):
        self.rooms = {}
        self.product_types = {}
        self.tags = {}
    
    def setup_categories(self):
        """Create or get room categories and product types"""
        print("=== Setting up Categories ===")
        
        # Room Categories
        room_data = [
            {'name': 'Living Room', 'slug': 'living-room', 'order': 1},
            {'name': 'Bedroom', 'slug': 'bedroom', 'order': 2},
            {'name': 'Dining Room', 'slug': 'dining-room', 'order': 3},
            {'name': 'Office', 'slug': 'office', 'order': 4},
            {'name': 'Outdoor', 'slug': 'outdoor', 'order': 5},
            {'name': 'Kids Room', 'slug': 'kids-room', 'order': 6},
        ]
        
        for room_info in room_data:
            room, created = RoomCategory.objects.get_or_create(
                slug=room_info['slug'],
                defaults={
                    'name': room_info['name'],
                    'order': room_info['order'],
                    'description': f'Beautiful furniture for your {room_info["name"].lower()}'
                }
            )
            self.rooms[room_info['name']] = room
            status = "✅ Created" if created else "✅ Exists"
            print(f"{status} room: {room_info['name']}")
        
        # Product Types
        type_data = [
            {'name': 'Sofas', 'slug': 'sofas', 'icon': '🛋️', 'order': 1},
            {'name': 'Chairs', 'slug': 'chairs', 'icon': '💺', 'order': 2},
            {'name': 'Tables', 'slug': 'tables', 'icon': '🪑', 'order': 3},
            {'name': 'Beds', 'slug': 'beds', 'icon': '🛏️', 'order': 4},
            {'name': 'Storage', 'slug': 'storage', 'icon': '🗄️', 'order': 5},
            {'name': 'Desks', 'slug': 'desks', 'icon': '💻', 'order': 6},
            {'name': 'Lighting', 'slug': 'lighting', 'icon': '💡', 'order': 7},
            {'name': 'Decor', 'slug': 'decor', 'icon': '🎨', 'order': 8},
        ]
        
        for type_info in type_data:
            product_type, created = ProductType.objects.get_or_create(
                slug=type_info['slug'],
                defaults={
                    'name': type_info['name'],
                    'icon': type_info['icon'],
                    'order': type_info['order'],
                    'description': f'Various {type_info["name"].lower()} for your home'
                }
            )
            self.product_types[type_info['name']] = product_type
            status = "✅ Created" if created else "✅ Exists"
            print(f"{status} product type: {type_info['name']}")
        
        # Tags
        tag_data = [
            {'name': 'On Sale', 'slug': 'on-sale', 'color': '#FF0000'},
            {'name': 'New Arrival', 'slug': 'new-arrival', 'color': '#00FF00'},
            {'name': 'Bestseller', 'slug': 'bestseller', 'color': '#0000FF'},
            {'name': 'Eco-Friendly', 'slug': 'eco-friendly', 'color': '#008000'},
            {'name': 'Luxury', 'slug': 'luxury', 'color': '#FFD700'},
            {'name': 'Modern', 'slug': 'modern', 'color': '#800080'},
            {'name': 'Minimalist', 'slug': 'minimalist', 'color': '#808080'},
            {'name': 'Vintage', 'slug': 'vintage', 'color': '#8B4513'},
        ]
        
        for tag_info in tag_data:
            tag, created = Tag.objects.get_or_create(
                slug=tag_info['slug'],
                defaults={
                    'name': tag_info['name'],
                    'color_code': tag_info['color']
                }
            )
            self.tags[tag_info['name']] = tag
            status = "✅ Created" if created else "✅ Exists"
            print(f"{status} tag: {tag_info['name']}")
    
    def create_products(self):
        """Create 20 sample furniture products"""
        print("\n=== Creating Sample Products ===")
        
        products_data = [
            # LIVING ROOM PRODUCTS
            {
                'name': 'Premium Leather 3-Seater Sofa',
                'slug': 'premium-leather-3-seater-sofa',
                'description': 'Luxurious genuine leather sofa with premium cushioning and sturdy hardwood frame. Perfect for modern living rooms.',
                'base_price': 85000.00,
                'sale_price': 75000.00,
                'rooms': ['Living Room'],
                'types': ['Sofas'],
                'tags': ['Luxury', 'On Sale', 'Bestseller'],
                'variations': [
                    {'color': 'brown', 'material': 'leather', 'sku': 'SOFA-BRN-LTH-001', 'modifier': 0},
                    {'color': 'black', 'material': 'leather', 'sku': 'SOFA-BLK-LTH-001', 'modifier': 5000},
                ]
            },
            {
                'name': 'Modern Fabric Sectional Sofa',
                'slug': 'modern-fabric-sectional-sofa',
                'description': 'Spacious L-shaped sectional sofa with soft fabric upholstery. Great for family gatherings and movie nights.',
                'base_price': 65000.00,
                'sale_price': 58000.00,
                'rooms': ['Living Room'],
                'types': ['Sofas'],
                'tags': ['Modern', 'On Sale'],
                'variations': [
                    {'color': 'gray', 'material': 'fabric', 'sku': 'SECTIONAL-GRY-FAB-001', 'modifier': 0},
                    {'color': 'navy', 'material': 'fabric', 'sku': 'SECTIONAL-NAV-FAB-001', 'modifier': 3000},
                ]
            },
            {
                'name': 'Glass Coffee Table with Storage',
                'slug': 'glass-coffee-table-storage',
                'description': 'Elegant glass-top coffee table with hidden storage compartment. Combines style with functionality.',
                'base_price': 15000.00,
                'sale_price': 12900.00,
                'rooms': ['Living Room'],
                'types': ['Tables'],
                'tags': ['Modern', 'Eco-Friendly'],
                'variations': [
                    {'color': 'black', 'material': 'glass', 'sku': 'TABLE-COFFEE-BLK-001', 'modifier': 0},
                ]
            },
            {
                'name': 'Accent Armchair',
                'slug': 'accent-armchair',
                'description': 'Comfortable accent chair perfect for reading corners or complementing your sofa set.',
                'base_price': 18000.00,
                'sale_price': 15000.00,
                'rooms': ['Living Room'],
                'types': ['Chairs'],
                'tags': ['Modern', 'On Sale'],
                'variations': [
                    {'color': 'gray', 'material': 'fabric', 'sku': 'CHAIR-ACCENT-GRY-001', 'modifier': 0},
                    {'color': 'blue', 'material': 'fabric', 'sku': 'CHAIR-ACCENT-BLU-001', 'modifier': 2000},
                ]
            },
            
            # BEDROOM PRODUCTS
            {
                'name': 'King Size Storage Bed',
                'slug': 'king-size-storage-bed',
                'description': 'Elegant king size bed with built-in storage drawers. Perfect for maximizing bedroom space.',
                'base_price': 45000.00,
                'sale_price': 39900.00,
                'rooms': ['Bedroom'],
                'types': ['Beds'],
                'tags': ['Bestseller', 'On Sale'],
                'variations': [
                    {'color': 'brown', 'material': 'wood', 'sku': 'BED-KING-BRN-001', 'modifier': 0},
                    {'color': 'white', 'material': 'wood', 'sku': 'BED-KING-WHT-001', 'modifier': 5000},
                ]
            },
            {
                'name': 'Queen Size Canopy Bed',
                'slug': 'queen-size-canopy-bed',
                'description': 'Romantic queen size canopy bed with elegant design. Creates a luxurious bedroom centerpiece.',
                'base_price': 55000.00,
                'sale_price': None,
                'rooms': ['Bedroom'],
                'types': ['Beds'],
                'tags': ['Luxury', 'New Arrival'],
                'variations': [
                    {'color': 'white', 'material': 'wood', 'sku': 'BED-QUEEN-WHT-001', 'modifier': 0},
                ]
            },
            {
                'name': '6-Drawer Dresser',
                'slug': '6-drawer-dresser',
                'description': 'Spacious 6-drawer dresser with smooth gliding drawers. Ample storage for clothing and accessories.',
                'base_price': 22000.00,
                'sale_price': 19900.00,
                'rooms': ['Bedroom'],
                'types': ['Storage'],
                'tags': ['Modern', 'On Sale'],
                'variations': [
                    {'color': 'brown', 'material': 'wood', 'sku': 'DRESSER-BRN-001', 'modifier': 0},
                    {'color': 'gray', 'material': 'wood', 'sku': 'DRESSER-GRY-001', 'modifier': 3000},
                ]
            },
            {
                'name': 'Bedside Nightstand',
                'slug': 'bedside-nightstand',
                'description': 'Compact bedside table with drawer and shelf. Perfect for lamps, books, and bedtime essentials.',
                'base_price': 8000.00,
                'sale_price': 6900.00,
                'rooms': ['Bedroom'],
                'types': ['Tables'],
                'tags': ['Modern', 'On Sale'],
                'variations': [
                    {'color': 'brown', 'material': 'wood', 'sku': 'NIGHTSTAND-BRN-001', 'modifier': 0},
                ]
            },
            
            # DINING ROOM PRODUCTS
            {
                'name': '6-Seater Dining Table Set',
                'slug': '6-seater-dining-table-set',
                'description': 'Complete 6-seater dining set with table and matching chairs. Perfect for family meals and entertaining.',
                'base_price': 55000.00,
                'sale_price': 49000.00,
                'rooms': ['Dining Room'],
                'types': ['Tables', 'Chairs'],
                'tags': ['Bestseller', 'On Sale'],
                'variations': [
                    {'color': 'brown', 'material': 'wood', 'sku': 'DINING-BRN-001', 'modifier': 0},
                    {'color': 'black', 'material': 'wood', 'sku': 'DINING-BLK-001', 'modifier': 5000},
                ]
            },
            {
                'name': 'Extendable Dining Table',
                'slug': 'extendable-dining-table',
                'description': 'Smart extendable table that seats 6-8 people. Perfect for hosting dinner parties and family gatherings.',
                'base_price': 38000.00,
                'sale_price': None,
                'rooms': ['Dining Room'],
                'types': ['Tables'],
                'tags': ['Modern', 'New Arrival'],
                'variations': [
                    {'color': 'brown', 'material': 'wood', 'sku': 'TABLE-EXTEND-BRN-001', 'modifier': 0},
                ]
            },
            {
                'name': 'Upholstered Dining Chairs (Set of 4)',
                'slug': 'upholstered-dining-chairs',
                'description': 'Set of 4 comfortable upholstered dining chairs with padded seats. Ergonomically designed for long meals.',
                'base_price': 28000.00,
                'sale_price': 24000.00,
                'rooms': ['Dining Room'],
                'types': ['Chairs'],
                'tags': ['On Sale', 'Modern'],
                'variations': [
                    {'color': 'gray', 'material': 'fabric', 'sku': 'CHAIR-DINING-GRY-001', 'modifier': 0},
                    {'color': 'beige', 'material': 'fabric', 'sku': 'CHAIR-DINING-BEI-001', 'modifier': 2000},
                ]
            },
            {
                'name': 'Bar Stool Set',
                'slug': 'bar-stool-set',
                'description': 'Set of 2 modern bar stools with comfortable seating and sturdy construction. Perfect for kitchen islands.',
                'base_price': 12000.00,
                'sale_price': 9900.00,
                'rooms': ['Dining Room'],
                'types': ['Chairs'],
                'tags': ['On Sale', 'Modern'],
                'variations': [
                    {'color': 'black', 'material': 'metal', 'sku': 'STOOL-BLK-001', 'modifier': 0},
                ]
            },
            
            # OFFICE PRODUCTS
            {
                'name': 'Executive Office Desk',
                'slug': 'executive-office-desk',
                'description': 'Spacious executive desk with multiple drawers and cable management. Perfect for home office or corporate use.',
                'base_price': 32000.00,
                'sale_price': 28500.00,
                'rooms': ['Office'],
                'types': ['Desks'],
                'tags': ['Modern', 'On Sale'],
                'variations': [
                    {'color': 'brown', 'material': 'wood', 'sku': 'DESK-EXEC-BRN-001', 'modifier': 0},
                    {'color': 'black', 'material': 'wood', 'sku': 'DESK-EXEC-BLK-001', 'modifier': 4000},
                ]
            },
            {
                'name': 'Ergonomic Office Chair',
                'slug': 'ergonomic-office-chair',
                'description': 'Professional ergonomic chair with lumbar support, adjustable height, and breathable mesh back.',
                'base_price': 25000.00,
                'sale_price': 22000.00,
                'rooms': ['Office'],
                'types': ['Chairs'],
                'tags': ['Eco-Friendly', 'On Sale'],
                'variations': [
                    {'color': 'black', 'material': 'mesh', 'sku': 'CHAIR-OFFICE-BLK-001', 'modifier': 0},
                    {'color': 'gray', 'material': 'mesh', 'sku': 'CHAIR-OFFICE-GRY-001', 'modifier': 0},
                ]
            },
            {
                'name': 'Filing Cabinet',
                'slug': 'filing-cabinet',
                'description': '2-drawer filing cabinet with lock for secure document storage. Fits letter and A4 size documents.',
                'base_price': 15000.00,
                'sale_price': 12900.00,
                'rooms': ['Office'],
                'types': ['Storage'],
                'tags': ['Modern', 'On Sale'],
                'variations': [
                    {'color': 'black', 'material': 'metal', 'sku': 'CABINET-BLK-001', 'modifier': 0},
                    {'color': 'gray', 'material': 'metal', 'sku': 'CABINET-GRY-001', 'modifier': 2000},
                ]
            },
            {
                'name': 'Bookshelf Unit',
                'slug': 'bookshelf-unit',
                'description': '5-shelf bookcase with adjustable shelves. Perfect for office, living room, or bedroom storage.',
                'base_price': 18000.00,
                'sale_price': 15900.00,
                'rooms': ['Office', 'Living Room'],
                'types': ['Storage'],
                'tags': ['Modern', 'On Sale'],
                'variations': [
                    {'color': 'brown', 'material': 'wood', 'sku': 'SHELF-BRN-001', 'modifier': 0},
                    {'color': 'white', 'material': 'wood', 'sku': 'SHELF-WHT-001', 'modifier': 3000},
                ]
            },
            
            # OUTDOOR PRODUCTS
            {
                'name': 'Patio Dining Set',
                'slug': 'patio-dining-set',
                'description': '6-piece outdoor dining set with table and chairs. Weather-resistant materials for long-lasting use.',
                'base_price': 45000.00,
                'sale_price': 39900.00,
                'rooms': ['Outdoor'],
                'types': ['Tables', 'Chairs'],
                'tags': ['On Sale', 'Eco-Friendly'],
                'variations': [
                    {'color': 'brown', 'material': 'rattan', 'sku': 'PATIO-BRN-001', 'modifier': 0},
                ]
            },
            {
                'name': 'Outdoor Lounge Chair',
                'slug': 'outdoor-lounge-chair',
                'description': 'Comfortable outdoor lounge chair with adjustable back. Perfect for poolside or garden relaxation.',
                'base_price': 12000.00,
                'sale_price': 9900.00,
                'rooms': ['Outdoor'],
                'types': ['Chairs'],
                'tags': ['On Sale', 'Modern'],
                'variations': [
                    {'color': 'gray', 'material': 'rattan', 'sku': 'LOUNGE-GRY-001', 'modifier': 0},
                    {'color': 'blue', 'material': 'rattan', 'sku': 'LOUNGE-BLU-001', 'modifier': 2000},
                ]
            },
            
            # KIDS ROOM PRODUCTS
            {
                'name': 'Kids Bunk Bed',
                'slug': 'kids-bunk-bed',
                'description': 'Safe and fun bunk bed for kids room. Includes guard rails and sturdy ladder. Saves space in shared rooms.',
                'base_price': 35000.00,
                'sale_price': 29900.00,
                'rooms': ['Kids Room'],
                'types': ['Beds'],
                'tags': ['On Sale', 'Eco-Friendly'],
                'variations': [
                    {'color': 'white', 'material': 'wood', 'sku': 'BUNK-WHT-001', 'modifier': 0},
                    {'color': 'blue', 'material': 'wood', 'sku': 'BUNK-BLU-001', 'modifier': 4000},
                    {'color': 'pink', 'material': 'wood', 'sku': 'BUNK-PINK-001', 'modifier': 4000},
                ]
            },
            {
                'name': 'Study Desk for Kids',
                'slug': 'study-desk-kids',
                'description': 'Adjustable height study desk perfect for growing children. Includes storage for books and supplies.',
                'base_price': 15000.00,
                'sale_price': 12900.00,
                'rooms': ['Kids Room', 'Office'],
                'types': ['Desks'],
                'tags': ['On Sale', 'Modern'],
                'variations': [
                    {'color': 'white', 'material': 'wood', 'sku': 'DESK-KIDS-WHT-001', 'modifier': 0},
                    {'color': 'blue', 'material': 'wood', 'sku': 'DESK-KIDS-BLU-001', 'modifier': 2000},
                ]
            },
        ]
        
        created_count = 0
        for product_info in products_data:
            # Set sale dates if there's a sale price
            sale_start = timezone.now() - timedelta(days=1) if product_info['sale_price'] else None
            sale_end = timezone.now() + timedelta(days=30) if product_info['sale_price'] else None
            
            product, created = Product.objects.get_or_create(
                slug=product_info['slug'],
                defaults={
                    'name': product_info['name'],
                    'description': product_info['description'],
                    'base_price': product_info['base_price'],
                    'sale_price': product_info['sale_price'],
                    'sale_start': sale_start,
                    'sale_end': sale_end,
                    'is_active': True
                }
            )
            
            if created:
                # Add room categories
                for room_name in product_info['rooms']:
                    room = self.rooms.get(room_name)
                    if room:
                        product.room_categories.add(room)
                
                # Add product types
                for type_name in product_info['types']:
                    product_type = self.product_types.get(type_name)
                    if product_type:
                        product.product_types.add(product_type)
                
                # Add tags
                for tag_name in product_info['tags']:
                    tag = self.tags.get(tag_name)
                    if tag:
                        product.tags.add(tag)
                
                # Create variations
                for variation_info in product_info['variations']:
                    ProductVariation.objects.create(
                        product=product,
                        sku=variation_info['sku'],
                        attributes=json.dumps(variation_info),
                        stock_quantity=random.randint(2, 10),
                        price_modifier=variation_info['modifier'],
                        is_active=True
                    )
                
                room_names = ", ".join(product_info['rooms'])
                type_names = ", ".join(product_info['types'])
                tag_names = ", ".join(product_info['tags'])
                
                print(f"✅ Created: {product_info['name']}")
                print(f"   Rooms: {room_names}")
                print(f"   Types: {type_names}")
                print(f"   Tags: {tag_names}")
                print(f"   Variations: {len(product_info['variations'])}")
                print()
                
                created_count += 1
            else:
                print(f"ℹ️ Exists: {product_info['name']}")
        
        return created_count
    
    def run(self):
        """Run the complete setup process"""
        print("🛋️ SOFA HUB Sample Products Creator")
        print("=" * 60)
        
        self.setup_categories()
        created_count = self.create_products()
        
        # Summary
        print("=" * 60)
        print("📊 CREATION SUMMARY:")
        print(f"🏠 Room Categories: {len(self.rooms)}")
        print(f"📦 Product Types: {len(self.product_types)}")
        print(f"🏷️ Tags: {len(self.tags)}")
        print(f"🛋️ Products Created: {created_count}")
        
        # Count variations
        total_variations = ProductVariation.objects.count()
        print(f"🎨 Total Variations: {total_variations}")
        print("=" * 60)
        print("✅ Sample data creation completed successfully!")
        print("🚀 Your store is now ready with realistic furniture products!")

def main():
    creator = SampleProductCreator()
    creator.run()

if __name__ == "__main__":
    main()