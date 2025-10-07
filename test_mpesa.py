import os
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sofahub_backend.settings')
django.setup()

from orders.services import get_mpesa_access_token, initiate_mpesa_payment, confirm_mpesa_payment
from orders.models import Order
from products.models import Product, ProductVariation, Category, Tag
from cart.models import Cart, CartItem


def test_mpesa_integration():
    print("=== Testing M-Pesa Integration ===\n")

    # Test 1: Get access token
    print("1. Testing access token retrieval...")
    access_token = get_mpesa_access_token()
    if access_token:
        print(f"   ✓ Success! Access token: {access_token[:20]}...")
    else:
        print("   ✗ Failed to get access token")
        return False

    # Test 2: Create test data
    print("\n2. Creating test data...")

    # Create a test category
    category, created = Category.objects.get_or_create(
        name="Test Furniture",
        defaults={'slug': 'test-furniture', 'description': 'Test category'}
    )

    # Create a test tag
    tag, created = Tag.objects.get_or_create(
        name="Test Product",
        defaults={'slug': 'test-product', 'color_code': '#FF0000'}
    )

    # Create a test product
    product, created = Product.objects.get_or_create(
        name="Test Sofa",
        defaults={
            'slug': 'test-sofa',
            'description': 'A test sofa for M-Pesa testing',
            'base_price': 10000.00,
            'sale_price': 0.00,
            'is_active': True
        }
    )
    product.categories.add(category)
    product.tags.add(tag)

    # Create a test variation
    variation, created = ProductVariation.objects.get_or_create(
        product=product,
        sku="TEST-SOFA-001",
        defaults={
            'attributes': '{"color": "Red", "material": "Fabric"}',
            'stock_quantity': 10,
            'price_modifier': 0,
            'is_active': True
        }
    )

    print(f"   ✓ Created test product: {product.name}")
    print(f"   ✓ Created test variation: {variation.sku}")

    # Test 3: Create a test cart
    print("\n3. Creating test cart...")
    cart, created = Cart.objects.get_or_create(session_id="test_session_123")
    if created:
        cart_item = CartItem.objects.create(cart=cart, variation=variation, quantity=1)
        print(f"   ✓ Created test cart with item: {cart_item.variation.product.name}")
    else:
        print("   ✓ Using existing test cart")

    # Test 4: Initiate M-Pesa payment
    print("\n4. Testing M-Pesa payment initiation...")
    phone_number = "254741504911"  # Sandbox test number
    amount = 100  # 100 KES for testing
    order_id = 1  # Test order ID

    response = initiate_mpesa_payment(phone_number, amount, order_id)
    print(f"   M-Pesa Response: {json.dumps(response, indent=2)}")

    if response.get('ResponseCode') == '0':
        print("   ✓ M-Pesa payment initiated successfully!")
        checkout_request_id = response.get('CheckoutRequestID')
        print(f"   Checkout Request ID: {checkout_request_id}")

        # Test 5: Check payment status (optional)
        print("\n5. Testing payment status check...")
        status_response = confirm_mpesa_payment(checkout_request_id)
        print(f"   Status Response: {json.dumps(status_response, indent=2)}")

    else:
        print("   ✗ Failed to initiate M-Pesa payment")
        error_message = response.get('errorMessage', response.get('error', 'Unknown error'))
        print(f"   Error: {error_message}")
        return False

    print("\n=== M-Pesa Integration Test Complete ===")
    return True


if __name__ == "__main__":
    test_mpesa_integration()