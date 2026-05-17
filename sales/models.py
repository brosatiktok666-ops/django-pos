from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

# ១. បង្កើតតារាងប្រភេទក្រុមផលិតផល
class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

# ២. តារាងផលិតផល (Update ថ្មី)
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'អាហារ និងភេសជ្ជៈ'),
        ('electronics', 'អេឡិចត្រូនិក'),
        ('clothing', 'សម្លៀកបំពាក់'),
        ('household', 'គ្រឿងសង្ហារឹម'),
        ('other', 'ផ្សេងៗ'),
    ]

    name = models.CharField(max_length=200)
    # ប្រើ ForeignKey ដើម្បីភ្ជាប់ទៅ Category model
    category_group = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    # រក្សាទុក choice ចាស់ផងដែរ
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    stock = models.PositiveIntegerField(default=0)
    barcode = models.CharField(max_length=50, unique=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} — ${self.price}"

    class Meta:
        ordering = ['name']

# ៣. តារាងវិក្កយបត្រ (Order)
class Order(models.Model):
    STATUS_CHOICES = [
        ('open', 'បានបើក'),
        ('paid', 'បានបង់'),
        ('refunded', 'បានសង'),
        ('cancelled', 'បានលុបចោល'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'សាច់ប្រាក់'),
        ('khqr', 'KHQR / ធនាគារ'),
    ]

    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def update_total(self):
        subtotal = sum(Decimal(str(item.unit_price)) * item.quantity for item in self.items.all())
        total = subtotal
        
        if hasattr(self, 'discount'):
            discount_val = Decimal(str(self.discount.amount))
            if self.discount.discount_type == 'percent':
                discount_amount = total * (discount_val / Decimal('100'))
                total -= discount_amount
            else:
                total -= discount_val
        
        self.total_amount = max(total, Decimal('0'))
        self.save()

    @property
    def total(self):
        return self.total_amount

    def __str__(self):
        return f"Order #{self.pk} ({self.status})"

    class Meta:
        ordering = ['-created_at']

# ៤. តារាងបញ្ចុះតម្លៃ (Discount)
class Discount(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='discount')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount_type = models.CharField(
        max_length=10, 
        choices=[('fixed', '$'), ('percent', '%')], 
        default='fixed'
    )
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        symbol = "%" if self.discount_type == 'percent' else "$"
        return f"{self.amount}{symbol} ({self.description})"

# ៥. តារាងទំនិញក្នុងវិក្កយបត្រ (OrderItem)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)
        self.order.update_total()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.update_total()

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"