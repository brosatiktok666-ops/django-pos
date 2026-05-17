# sales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ── Part 1: Views សម្រាប់បញ្ជីផលិតផល និងរបាយការណ៍ ────────────────────────
    path('products/',             views.product_list,   name='product_list'),
    path('products/<int:pk>/',    views.product_detail, name='product_detail'),
    path('orders/',               views.order_list,     name='order_list'),
    path('orders/mine/',          views.my_orders,      name='my_orders'),

    # ── Part 2: Views សម្រាប់ដំណើរការលក់ (POS) ─────────────────────────────
    path('orders/new/',            views.create_order,   name='create_order'),
    path('orders/<int:pk>/items/', views.add_item,       name='add_item'),

    # ── Part 3: KHQR Integration (ស្កែនបង់ប្រាក់អូតូ) ────────────────────────
    # ប្រើបានទាំងឈ្មោះ 'show_khqr' និង 'generate_khqr' ដើម្បីបង្ការ Error
    path('order/<int:order_id>/khqr/', views.show_khqr_view, name='show_khqr'),
    path('order/<int:order_id>/generate_khqr/', views.show_khqr_view, name='generate_khqr'),

    # ── Part 4: PDF Export (ទាញយកវិក្កយបត្រ) ────────────────────────────────
    path('order/<int:order_id>/pdf/', views.export_pdf, name='export_pdf'),
]