from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Discount

# ១. ចុះឈ្មោះ Category ឱ្យបង្ហាញក្នុង Admin
admin.site.register(Category)

# ២. សម្រាប់គ្រប់គ្រងផលិតផល
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # បង្ហាញទាំង category_group (Model ថ្មី) និង category (Choices ចាស់)
    list_display   = ['name', 'category_group', 'category', 'price', 'stock', 'is_active']
    list_filter    = ['category_group', 'category', 'is_active']
    search_fields  = ['name', 'barcode']
    ordering       = ['name']

# ៣. បង្កើត Inline សម្រាប់បង្ហាញទំនិញក្នុងវិក្កយបត្រ (បង្ហាញក្នុងទំព័រ Order តែម្តង)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product', 'quantity', 'unit_price'] 
    extra = 1 # ចំនួនជួរដែលបង្ហាញសម្រាប់ថែមទំនិញថ្មី

# ៤. សម្រាប់គ្រប់គ្រងការបញ្ជាទិញ (Order)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # បន្ថែម 'display_products' ដើម្បីបង្ហាញឈ្មោះទំនិញក្នុងតារាង
    list_display  = ['id', 'cashier', 'status', 'payment_method', 'display_products', 'total_amount', 'created_at'] 
    list_filter   = ['status', 'created_at', 'payment_method']
    search_fields = ['id', 'cashier__username']
    ordering      = ['-created_at']
    inlines       = [OrderItemInline]

    # មុខងារសម្រាប់ទាញឈ្មោះទំនិញក្នុងវិក្កយបត្រមកបង្ហាញក្នុងតារាងសរុប
    def display_products(self, obj):
        order_items = obj.items.all()
        if order_items.exists():
            return ", ".join([item.product.name for item in order_items])
        return "គ្មានទំនិញ"

    # ប្តូរឈ្មោះ Header ក្នុង Admin ឱ្យទៅជាភាសាខ្មែរ
    display_products.short_description = 'ឈ្មោះទំនិញដែលបានទិញ'

# ៥. សម្រាប់គ្រប់គ្រងការបញ្ចុះតម្លៃ
@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['order', 'description', 'amount', 'discount_type']

# ៦. ចុះឈ្មោះ OrderItem ធម្មតា (បើបងចង់កែទំនិញដាច់ដោយឡែក)
admin.site.register(OrderItem)