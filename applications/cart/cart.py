from decimal import Decimal
from applications.products.models import Product
import hashlib

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart
    
    def _generate_item_key(self, product_id, note=""):
        """Genera una clave única basada en product_id + nota"""
        # Crear un hash único para la combinación producto+nota
        unique_string = f"{product_id}_{note}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:10]
    
    def add(self, product, quantity=1, note="", override_quantity=False):
        """Agrega un producto al carrito, tratando producto+nota como único"""
        item_key = self._generate_item_key(product.id, note)
        
        if item_key not in self.cart:
            # Nuevo item (producto + nota única)
            self.cart[item_key] = {
                "product_id": product.id,
                "name": product.name,
                "price": str(product.price),
                "quantity": quantity,
                "note": note,
                "item_key": item_key  # Guardamos la clave para referencia
            }
        else:
            # Item existente - actualizar cantidad
            if override_quantity:
                self.cart[item_key]["quantity"] = quantity
            else:
                self.cart[item_key]["quantity"] += quantity
            
            # Actualizar nota si se proporciona una nueva
            if note != self.cart[item_key]["note"]:
                self.cart[item_key]["note"] = note
        
        self.save()
    
    def remove(self, item_key):
        """Elimina un item específico del carrito usando su clave única"""
        if item_key in self.cart:
            del self.cart[item_key]
            self.save()
    
    def update_quantity(self, item_key, quantity):
        """Actualiza la cantidad de un item específico"""
        if item_key in self.cart and quantity > 0:
            self.cart[item_key]["quantity"] = quantity
            self.save()
    
    def get_item(self, item_key):
        """Obtiene un item específico del carrito"""
        return self.cart.get(item_key)
    
    def __iter__(self):
        """Iterar sobre los items con objetos de Product completos"""
        # Obtener todos los product_ids únicos
        product_ids = set(item["product_id"] for item in self.cart.values())
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {p.id: p for p in products}
        
        for item_key, item_data in self.cart.items():
            product = product_dict.get(item_data["product_id"])
            if product:
                item_data["product"] = product
                item_data["price"] = Decimal(item_data["price"])
                item_data["subtotal"] = item_data["price"] * item_data["quantity"]
                item_data["item_key"] = item_key  # Incluir la clave única
                yield item_data
    
    def __len__(self):
        """Cantidad total de items únicos en el carrito"""
        return len(self.cart)
    
    def get_total_quantity(self):
        """Cantidad total de productos (suma de cantidades)"""
        return sum(item["quantity"] for item in self.cart.values())
    
    def get_total(self):
        """Total del carrito"""
        return sum(
            Decimal(item["price"]) * item["quantity"]
            for item in self.cart.values()
        )
    
    def clear(self):
        """Vaciar carrito completamente"""
        self.session["cart"] = {}
        self.save()
    
    def save(self):
        self.session.modified = True