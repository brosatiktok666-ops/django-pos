import os
import qrcode
import base64
from io import BytesIO
from django.conf import settings
from django.contrib.staticfiles import finders
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template

# សម្រាប់ PDF
from xhtml2pdf import pisa
from .models import Category, Product, Order, OrderItem, Discount
from .forms import OrderItemForm

# --- ១. link_callback (សម្រាប់រូបភាព និង CSS ក្នុង PDF) ---
def link_callback(uri, rel):
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        s_url = settings.STATIC_URL
        s_root = settings.STATIC_ROOT
        if uri.startswith(s_url):
            path = os.path.join(s_root, uri.replace(s_url, ""))
        else:
            return uri
    if not os.path.isfile(path):
        raise Exception('public traversal are not allowed')
    return path

# --- ២. បញ្ជីផលិតផល (Update: បន្ថែម Categories) ---
@login_required
def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).order_by('name')
    
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_group_id=category_id)

    return render(request, 'sales/product_list.html', {
        'products': products,
        'categories': categories,
        'title': 'Product List'
    })

# --- ៣. ព័ត៌មានលម្អិតផលិតផល ---
@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'sales/product_detail.html', {
        'product': product,
        'title': f'Product Detail: {product.name}'
    })

# --- ៤. របាយការណ៍ការលក់ទាំងអស់ ---
@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    total_revenue = Order.objects.filter(status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
    return render(request, 'sales/order_list.html', {
        'orders': orders,
        'total_revenue': total_revenue,
        'title': 'All Sales Report'
    })

# --- ៥. การលក់របស់ខ្ញុំ ---
@login_required
def my_orders(request):
    orders = Order.objects.filter(cashier=request.user).order_by('-created_at')
    total_revenue = orders.filter(status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
    return render(request, 'sales/order_list.html', {
        'orders': orders,
        'total_revenue': total_revenue,
        'title': 'My Sales'
    })

# --- ៦. បង្កើតវិក្កយបត្រថ្មី ---
@login_required
def create_order(request):
    order = Order.objects.create(cashier=request.user, status='open')
    return redirect('add_item', pk=order.pk)

# --- ៧. ប្រព័ន្ធ POS (កន្លែងបន្ថែមទំនិញ និងគិតលុយ) ---
@login_required
def add_item(request, pk):
    order = get_object_or_404(Order, pk=pk)
    products = Product.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        if 'cancel_order' in request.POST:
            order.status = 'cancelled'
            order.save()
            messages.warning(request, f"Order #{order.pk} cancelled!")
            return redirect('order_list')

        if 'apply_discount' in request.POST:
            amount = request.POST.get('discount_amount', 0)
            d_type = request.POST.get('discount_type', 'fixed')
            if amount and float(amount) > 0:
                Discount.objects.update_or_create(
                    order=order,
                    defaults={'amount': amount, 'discount_type': d_type, 'description': 'Special Discount'}
                )
                order.update_total()
                messages.success(request, "Discount applied!")
            return redirect('add_item', pk=order.pk)

        if 'mark_paid' in request.POST:
            if order.items.count() == 0:
                messages.error(request, "Invoice is empty!")
            else:
                method = request.POST.get('payment_method', 'cash')
                order.status = 'paid'
                order.payment_method = method
                order.is_paid = True
                order.save()
                messages.success(request, f"Order #{order.pk} paid via {method}!")
                return redirect('order_list')
            return redirect('add_item', pk=order.pk)

        if order.status == 'open':
            item_form = OrderItemForm(request.POST)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.order = order
                if item.product.stock < item.quantity:
                    messages.error(request, f"Out of stock: {item.product.name}")
                else:
                    item.unit_price = item.product.price
                    item.save()
                    product = item.product
                    product.stock -= item.quantity
                    product.save()
                    order.update_total()
                    messages.success(request, f"Added {product.name}")
                return redirect('add_item', pk=order.pk)
    else:
        item_form = OrderItemForm()

    return render(request, 'sales/add_item.html', {
        'order': order,
        'item_form': item_form,
        'items': order.items.select_related('product'),
        'products': products,
        'title': f'POS: #{order.pk}'
    })

# --- ៨. បង្កើត ABA KHQR --- 
@login_required
def show_khqr_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    bank_account = "004766663" 
    merchant_name = "MAO SARIN" 
    amount = "{:.2f}".format(order.total_amount) 
    
    payload = (
        "000201" 
        "010212" 
        f"29380010A0000007180110{bank_account}0206ABA001" 
        "52045999" 
        "5303840" 
        f"54{len(amount):02d}{amount}" 
        "5802KH" 
        f"59{len(merchant_name):02d}{merchant_name}" 
        "6005Phnom" 
        "6304"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'sales/khqr_page.html', {
        'order': order,
        'qr_image': qr_image_base64,
        'title': f'Scan to Pay - #{order.id}'
    })

# --- ៩. បង្កើតវិក្កយបត្រជា PDF (កែសម្រួលបន្ថែមការគណនាបញ្ចុះតម្លៃ) ---
@login_required
def export_pdf(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    template_path = 'sales/invoice_pdf.html'
    
    # គណនាតម្លៃសរុបពិតប្រាកដមុនពេលបញ្ចុះតម្លៃ (តម្លៃពេញ)
    subtotal_before_discount = sum(item.unit_price * item.quantity for item in order.items.all())
    
    # គណនាចំនួនទឹកប្រាក់ដែលបានបញ្ចុះជាលុយ ($) ដើម្បីបង្ហាញលើវិក្កយបត្រ
    discount_amount_calculated = 0
    discount_display = "0.00"
    
    if hasattr(order, 'discount') and order.discount:
        amount = order.discount.amount
        if order.discount.discount_type == 'percent':
            discount_amount_calculated = float(subtotal_before_discount) * (float(amount) / 100)
            discount_display = f"{amount}%"
        else:
            discount_amount_calculated = float(amount)
            discount_display = f"${amount}"

    context = {
        'order': order,
        'subtotal_before_discount': subtotal_before_discount,
        'discount_display': discount_display,
        'discount_amount_calculated': discount_amount_calculated,
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html, 
        dest=response, 
        link_callback=link_callback
    )
    
    if pisa_status.err:
        return HttpResponse(f'Error creating PDF for Order #{order.id}', status=500)
    
    return response