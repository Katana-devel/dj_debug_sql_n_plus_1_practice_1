from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Product category with optional parent for hierarchy."""
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model with intentional issues for practice:
    - No index on created_at (for EXPLAIN ANALYZE exercise)
    - Large description field (for defer() practice)
    """
    name = models.CharField(max_length=200)
    description = models.TextField()  # Large field - use defer() to optimize
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)  # No index - intentional

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Order model with intentional issues:
    - No index on status (for EXPLAIN ANALYZE exercise)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )  # No index - intentional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    @property
    def total(self):
        """Calculate order total - triggers N+1 if items not prefetched."""
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    """Order line item linking orders to products."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity
