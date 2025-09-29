from django.shortcuts import redirect, get_object_or_404, render
from applications.products.models import Product
from .cart import Cart
from django.views.decorators.http import require_POST
from applications.products.forms import AddToCartForm
from .models import Order, OrderItem

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

def remove_from_cart(request, item_key):
    """Elimina un item específico usando su clave única"""
    cart = Cart(request)
    cart.remove(item_key)
    return redirect("cart:cart_detail")

@require_POST
def update_cart_item(request, item_key):
    """Actualiza la cantidad de un item específico"""
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update_quantity(item_key, quantity)
    return redirect("cart:cart_detail")

def cart_detail(request):
    cart = Cart(request)
    
    if request.method == "POST":
        customer_name = request.POST.get('customer_name')
        if customer_name and cart:
            # Crear el pedido
            order = Order.objects.create(
                customer_name=customer_name,
                total=cart.get_total()
            )
            
            # Crear los items del pedido
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price'],
                    note=item.get('note', '')
                )
            
            # Limpiar el carrito
            cart.clear()
            
            # Redirigir a la página de éxito
            return redirect('cart:order_success', order_id=order.id)
    
    return render(request, "cart/cart_detail.html", {"cart": cart})

def order_success(request, order_id):
    """Vista para mostrar el comprobante del pedido confirmado"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, "cart/order_success.html", {"order": order})

def home(request):
    return render(request, "cart/home.html")