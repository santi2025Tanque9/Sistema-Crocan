from django.db import models
from django.conf import settings
from applications.products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('preparing', 'En preparación'),
        ('ready', 'Listo para entregar'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Para clientes regulares (sin cuenta)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Para clientes socios (con cuenta) - usando el modelo compartido
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Esto apunta a 'users.Usuario'
        on_delete=models.SET_NULL, 
        blank=True, null=True, 
        related_name='orders'
    )
    
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        if self.customer:
            return f"Pedido #{self.id} - {self.customer.get_full_name()}"
        return f"Pedido #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = "Item de pedido"
        verbose_name_plural = "Items de pedido"

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"