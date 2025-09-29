from django.shortcuts import render
from django.http import HttpResponse
from .models import Category, Product
from django.shortcuts import render, get_object_or_404
from .forms import AddToCartForm

def product_list(request, category_id=None):
    categories = Category.objects.all()
    
    if category_id:
        products = Product.objects.filter(category_id=category_id, is_active=True)
        current_category = Category.objects.get(id=category_id)
    else:
        current_category = categories.first()
        products = Product.objects.filter(category=current_category, is_active=True) if current_category else []

    context = {
        "categories": categories,
        "products": products,
        "current_category": current_category,
    }
    return render(request, "products/product_list.html", context)

# Podemos comentar temporalmente la vista de detalle
# def product_detail(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart_product_form = AddToCartForm()
#     return render(request, "products/product_detail.html", {"product": product, 'cart_product_form': cart_product_form})