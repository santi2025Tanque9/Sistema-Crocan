from django.shortcuts import redirect, get_object_or_404, render
from applications.products.models import Product
from .cart import Cart
from django.views.decorators.http import require_POST
from applications.products.forms import AddToCartForm
from .models import Order, OrderItem

from applications.users.models import Usuario

#Para el login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings

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
        
        # Determinar si es socio o regular
        is_socio = 'customer_id' in request.session
        customer = None
        
        if is_socio:
            # Cliente socio - usar el de la sesión
            try:
                customer = Usuario.objects.get(id=request.session['customer_id'])
                customer_name = None
            except Usuario.DoesNotExist:
                # Si el usuario fue eliminado, limpiar sesión
                if 'customer_id' in request.session:
                    del request.session['customer_id']
                    del request.session['customer_name']
                    del request.session['customer_points']
                    del request.session['customer_dni']
                customer = None
                is_socio = False
        else:
            # Cliente regular - validar que tenga nombre
            customer = None
            if not customer_name:
                return render(request, "cart/cart_detail.html", {
                    "cart": cart,
                    "error": "Por favor ingrese el nombre del cliente."
                })
        
        if cart:
            # Crear el pedido
            order = Order.objects.create(
                customer_name=customer_name,
                customer=customer,
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
            
            # Si es socio, acumular puntos (1 punto por cada $100 gastado)
            points_earned = 0
            if customer:
                points_earned = int(cart.get_total() / 100)
                customer.puntos += points_earned
                customer.save()
            
            # Guardar información para mostrar en order_success
            request.session['points_earned'] = points_earned
            request.session['was_socio'] = is_socio
            
            # Si era socio, guardar datos antes de cerrar sesión
            if is_socio:
                request.session['last_customer_name'] = request.session['customer_name']
                request.session['last_customer_dni'] = request.session['customer_dni']
                request.session['last_customer_points'] = customer.puntos  # Puntos actualizados
                
                # CERRAR SESIÓN DEL SOCIO automáticamente
                if 'customer_id' in request.session:
                    del request.session['customer_id']
                    del request.session['customer_name']
                    del request.session['customer_points']
                    del request.session['customer_dni']
            
            # Limpiar el carrito
            cart.clear()
            
            return redirect('cart:order_success', order_id=order.id)
    
    return render(request, "cart/cart_detail.html", {"cart": cart})

def order_success(request, order_id):
    """Vista para mostrar el comprobante del pedido confirmado"""
    order = get_object_or_404(Order, id=order_id)
    
    # Obtener información de la sesión
    points_earned = request.session.get('points_earned', 0)
    was_socio = request.session.get('was_socio', False)
    
    # Si era socio, obtener datos para mostrar
    last_customer_data = None
    if was_socio:
        last_customer_data = {
            'name': request.session.get('last_customer_name', ''),
            'dni': request.session.get('last_customer_dni', ''),
            'points': request.session.get('last_customer_points', 0),
            'points_earned': points_earned
        }
    
    # Limpiar datos temporales de la sesión
    if 'points_earned' in request.session:
        del request.session['points_earned']
    if 'was_socio' in request.session:
        del request.session['was_socio']
    if 'last_customer_name' in request.session:
        del request.session['last_customer_name']
    if 'last_customer_dni' in request.session:
        del request.session['last_customer_dni']
    if 'last_customer_points' in request.session:
        del request.session['last_customer_points']
    
    context = {
        "order": order,
        "points_earned": points_earned,
        "last_customer_data": last_customer_data,
    }
    return render(request, "cart/order_success.html", context)

def home(request):
    """Página de inicio - Selección de tipo de cliente"""
    return render(request, "cart/home.html")

def customer_login(request):
    """Vista para que los socios inicien sesión solo con DNI"""
    if request.method == "POST":
        dni = request.POST.get('dni')
        try:
            customer = Usuario.objects.get(dni=dni)
            # Guardar el cliente en la sesión (sin contraseña)
            request.session['customer_id'] = customer.id
            request.session['customer_name'] = customer.get_full_name()
            request.session['customer_points'] = customer.puntos
            request.session['customer_dni'] = customer.dni
            return redirect('products:product_list')
        except Usuario.DoesNotExist:
            return render(request, "cart/customer_login.html", {
                'error': 'Cliente no encontrado. Verifique su DNI.'
            })
    
    return render(request, "cart/customer_login.html")

def customer_logout(request):
    """Cerrar sesión del cliente socio"""
    # Limpiar la sesión
    if 'customer_id' in request.session:
        del request.session['customer_id']
        del request.session['customer_name']
        del request.session['customer_points']
        del request.session['customer_dni']
    return redirect('cart:home')