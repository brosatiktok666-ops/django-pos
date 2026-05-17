# sales/forms.py

from django import forms
from .models import OrderItem


class OrderItemForm(forms.ModelForm):
    """One line item to add to an order."""
    class Meta:
        model  = OrderItem
        fields = ['product', 'quantity']

    def clean_quantity(self):
        """Validation: quantity must be at least 1."""
        qty = self.cleaned_data['quantity']
        if qty < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return qty
# --- កូដថ្មី សម្រាប់ភារកិច្ចទី ២ (ឆែកស្តុកទំនិញ) ---
    # យើងគ្រាន់តែសរសេរបន្ថែមពីក្រោមបែបនេះ
    def clean_product(self):
        """Validation: ពិនិត្យថាផលិតផលត្រូវតែមានក្នុងស្តុក"""
        product = self.cleaned_data.get('product')
        
        # បើផលិតផលមានក្នុង Database តែចំនួនស្តុកស្មើ ០
        if product and product.stock == 0:
            # បោះ Error ប្រាប់ User
            raise forms.ValidationError("This product is out of stock.")
            
        return product