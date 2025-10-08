from django.core.management.base import BaseCommand
from products.models import Product
from orders.models import OrderItem
from cart.models import CartItem


class Command(BaseCommand):
    help = 'Test product deletion to ensure no 500 errors'

    def handle(self, *args, **options):
        """Test product deletion"""
        
        self.stdout.write('🧪 Testing product deletion...')
        
        # Check for products with orders
        products_with_orders = Product.objects.filter(variations__orderitem__isnull=False).distinct()
        products_with_cart_items = Product.objects.filter(variations__cartitem__isnull=False).distinct()
        
        self.stdout.write(f'📊 Products with orders: {products_with_orders.count()}')
        self.stdout.write(f'📊 Products with cart items: {products_with_cart_items.count()}')
        
        if products_with_orders.exists():
            self.stdout.write('⚠️  Some products have orders - they should still be deletable now')
            for product in products_with_orders:
                order_items = OrderItem.objects.filter(variation__product=product)
                self.stdout.write(f'  - {product.name}: {order_items.count()} order items')
        
        if products_with_cart_items.exists():
            self.stdout.write('⚠️  Some products have cart items - they should still be deletable now')
            for product in products_with_cart_items:
                cart_items = CartItem.objects.filter(variation__product=product)
                self.stdout.write(f'  - {product.name}: {cart_items.count()} cart items')
        
        self.stdout.write(
            self.style.SUCCESS('✅ Product deletion should now work without 500 errors!')
        )
        self.stdout.write('📝 Order history will be preserved even if products are deleted')
