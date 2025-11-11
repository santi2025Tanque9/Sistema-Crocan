from django.db import models
from applications.users.models import Usuario
from applications.products.models import Product
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('preparing', 'En preparación'),
        ('ready', 'Listo para retirar'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    
    customer = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    points_earned = models.IntegerField(default=0)  # Puntos ganados en esta compra
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.customer:
            return f"Pedido #{self.id} - {self.customer.get_full_name()}"
        return f"Pedido #{self.id} - {self.customer_name}"
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Precio en el momento de la compra
    note = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def get_subtotal(self):
        return self.quantity * self.price