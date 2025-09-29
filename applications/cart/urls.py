from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.home, name="home"),  # Nueva ruta para home
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("Carrito-Pedido/", views.cart_detail, name="cart_detail"),
    path("remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    
]