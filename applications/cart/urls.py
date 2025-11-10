from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.home, name="home"),
    path("customer-login/", views.customer_login, name="customer_login"),
    path("customer-logout/", views.customer_logout, name="customer_logout"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("Carrito-Pedido/", views.cart_detail, name="cart_detail"),
    path("remove/<str:item_key>/", views.remove_from_cart, name="remove_from_cart"),
    path("update/<str:item_key>/", views.update_cart_item, name="update_cart_item"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
]