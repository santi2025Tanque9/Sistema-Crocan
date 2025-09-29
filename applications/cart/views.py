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

def remove_from_cart(request, product_id):
    # Limpiar toda la sesión del carrito para este producto
    request.session.modified = True
    
    # Crear un nuevo carrito filtrado
    old_cart = request.session.get('cart', {})
    new_cart = {}
    target_id = str(product_id)
    
    for item_key, item_data in old_cart.items():
        should_keep = True
        
        # Verificar si este item pertenece al producto a eliminar
        if 'product_id' in item_data:
            if str(item_data['product_id']) == target_id:
                should_keep = False
        elif item_key.startswith(target_id + '_'):
            should_keep = False
        elif item_key == target_id:
            should_keep = False
        
        if should_keep:
            new_cart[item_key] = item_data
    
    request.session['cart'] = new_cart
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

def home(request):
    return render(request, "cart/home.html")

def order_success(request, order_id):
    """Vista para mostrar el comprobante del pedido confirmado"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, "cart/order_success.html", {"order": order})