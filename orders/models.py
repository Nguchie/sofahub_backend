from django.db import models
from products.models import ProductVariation
from cart.models import Cart


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('deposit_paid', 'Deposit Paid'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Customer information
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    # Shipping information
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_zip_code = models.CharField(max_length=20)

    # Order details
    cart_session = models.CharField(max_length=36)  # Reference to the cart session
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    # Payment information
    mpesa_transaction_id = models.CharField(max_length=50, blank=True, null=True)
    payment_confirmed = models.BooleanField(default=False)
    
    # Downpayment feature
    is_downpayment = models.BooleanField(default=True)  # Enable downpayment by default
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit_paid = models.BooleanField(default=False)
    balance_paid = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def calculate_downpayment(self):
        """Calculate deposit and remaining amounts
        
        Note: Downpayment is calculated on subtotal only (excludes delivery fees).
        Delivery fees are charged separately upon delivery.
        """
        if self.is_downpayment:
            # Half of the subtotal (delivery fees excluded)
            self.deposit_amount = self.subtotal / 2
            self.remaining_amount = self.subtotal - self.deposit_amount
        else:
            self.deposit_amount = self.subtotal
            self.remaining_amount = 0
        return self.deposit_amount, self.remaining_amount

    def get_payment_status(self):
        """Get current payment status"""
        if not self.is_downpayment:
            return "Full Payment" if self.payment_confirmed else "Pending"
        
        if self.balance_paid:
            return "Fully Paid"
        elif self.deposit_paid:
            return f"Deposit Paid (Balance: {self.remaining_amount})"
        else:
            return f"Deposit Required ({self.deposit_amount})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variation = models.ForeignKey(ProductVariation, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)  # Snapshot of product name at time of purchase
    variation_attributes = models.JSONField()  # Snapshot of variation attributes
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in Order #{self.order.id}"