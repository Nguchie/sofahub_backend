from django.db import models
from products.models import ProductVariation
from core.utils import generate_session_id


class Cart(models.Model):
    session_id = models.CharField(max_length=36, default=generate_session_id, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.session_id}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'variation']

    def __str__(self):
        return f"{self.quantity} x {self.variation} in {self.cart}"

    @property
    def unit_price(self):
        return self.variation.price

    @property
    def total_price(self):
        return self.unit_price * self.quantity