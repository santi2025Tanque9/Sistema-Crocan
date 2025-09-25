from django.shortcuts import redirect, get_object_or_404, render
from applications.products.models import Product
from .cart import Cart
from django.views.decorators.http import require_POST
from applications.products.forms import AddToCartForm

@require_POST
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = AddToCartForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(
                product=product,
                quantity=cd["quantity"],
                note=cd["note"],
                override_quantity=cd["override_quantity"],
            )
    return redirect("cart:cart_detail")

@require_POST
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")

def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/cart_detail.html", {"cart": cart})
