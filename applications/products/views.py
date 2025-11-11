from django.shortcuts import render
from django.http import HttpResponse
from .models import Category, Product
from django.shortcuts import render, get_object_or_404
from .forms import AddToCartForm
from applications.users.models import Usuario

def product_list(request, category_id=None):
    categories = Category.objects.all()
    
    if category_id:
        products = Product.objects.filter(category_id=category_id, is_active=True)
        current_category = Category.objects.get(id=category_id)
    else:
        current_category = categories.first()
        products = Product.objects.filter(category=current_category, is_active=True) if current_category else []

    # Verificar si hay un socio en sesión y obtener sus datos completos
    customer_data = None
    if 'customer_id' in request.session:
        try:
            customer = Usuario.objects.get(id=request.session['customer_id'])
            customer_data = {
                'name': customer.get_full_name(),
                'dni': customer.dni,
                'points': customer.puntos
            }
        except Usuario.DoesNotExist:
            # Si el usuario no existe, limpiar la sesión
            if 'customer_id' in request.session:
                del request.session['customer_id']
                del request.session['customer_name']
                del request.session['customer_points']
                del request.session['customer_dni']

    context = {
        "categories": categories,
        "products": products,
        "current_category": current_category,
        "customer_data": customer_data,
    }
    return render(request, "products/product_list.html", context)
# Podemos comentar temporalmente la vista de detalle
# def product_detail(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart_product_form = AddToCartForm()
#     return render(request, "products/product_detail.html", {"product": product, 'cart_product_form': cart_product_form})