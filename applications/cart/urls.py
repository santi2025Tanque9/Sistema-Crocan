from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("Carrito-Pedido/", views.cart_detail, name="cart_detail"),  # para ver el carrito
    path("remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
]