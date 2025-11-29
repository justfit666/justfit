# shop/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
# shop/models.py
from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User




class SizeType(models.Model):
    name = models.CharField(max_length=50)
    sizes = models.JSONField(default=list)  # e.g., ["S","M","L","XL"]

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    size_type = models.ForeignKey(SizeType, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def total_quantity(self):
        return sum(v.quantity for v in self.variants.all())

    @property
    def total_quantity_available(self):
        return sum(v.availability_count for v in self.variants.all())


    @property
    def first_image_url(self):
        first_img = self.images.first()
        if first_img:
            return first_img.image.url
        return ""

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    availability_count = models.PositiveIntegerField(default=0)
    in_delivery = models.PositiveIntegerField(default=0)  # NEW FIELD

    def save(self, *args, **kwargs):
        # Only set availability_count on FIRST creation
        if self.pk is None:
            self.availability_count = self.quantity
            # in_delivery defaults to 0 automatically
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/")

    def __str__(self):
        return self.product.name



class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user} ❤️ {self.product}"
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.variant.product.selling_price * self.quantity

    def __str__(self):
        return f"{self.user} Cart → {self.variant}"

class Order(models.Model):

    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="in_progress"
    )

    comment = models.TextField(blank=True, null=True)
    cutomer_name = models.TextField(blank=True, null=True)

    # Track old status
    _old_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_status = self.status

    def save(self, *args, **kwargs):

        # Detect status change → Restock only when moving TO cancelled
        if self.pk and self._old_status != "cancelled" and self.status == "cancelled":
            for item in self.items.all():
                variant = item.variant
                if variant:
                    variant.availability_count += item.quantity
                    variant.save()

        super().save(*args, **kwargs)
        self._old_status = self.status  # update for next change

    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price




# shop/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Expense(models.Model):

    # Only admin users (is_staff=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_staff': True},
        related_name="expenses"
    )

    TYPE_CHOICES = [
        ("Product", "Product"),
        ("Extra offer", "Extra offer"),
        ("Ads", "Ads"),
        ("Other", "Other"),
        ("Extra gain", "Extra gain"),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default="Product")

    comment = models.TextField(blank=True, null=True)
    

    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user} | {self.amount} | {self.type} | {self.date}"

    class Meta:
        ordering = ['-date']

class Credit(models.Model):

    # Only admin users (is_staff=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_staff': True},
        related_name="credits"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    comment = models.TextField(blank=True, null=True)

    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user} | {self.amount} | {self.date}"

    class Meta:
        ordering = ['-date']
