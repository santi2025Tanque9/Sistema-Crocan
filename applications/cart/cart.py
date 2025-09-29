from decimal import Decimal
from applications.products.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            # Estructura del carrito
            cart = self.session["cart"] = {}
        self.cart = cart
        
        
    def add(self, product, quantity=1, note="", override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                "name": product.name,
                "price": str(product.price),
                "quantity": 0,
                "note": note,
            }
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity # Si ya esta en el carrito y override_quantity=True reemplaza la cantidad
        else:
            self.cart[product_id]["quantity"] += quantity #Si ya esta en el carrito y override_quantity=False, suma la cantidad a la existente.
        
        if note:
            self.cart[product_id]["note"] = note
        
        self.save()
        
        
    def remove(self, product):
        """Elimina un producto del carrito"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
            
    def update_note(self, product, note):
        """Cambia la nota de un producto"""
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]["note"] = note
            self.save()
            
    def __iter__(self):
        """Iterar sobre los items con objetos de Product"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids) #Obtengo los productos que este en el carrito
        for product in products:
            item = self.cart[str(product.id)]
            item["product"] = product
            item["price"] = Decimal(item["price"])
            item["subtotal"] = item["price"] * item["quantity"]
            yield item
            
    def __len__(self):
        """Cantidad total de items"""
        return sum(item["quantity"] for item in self.cart.values())

    def get_total(self):
        """Total del carrito"""
        return sum(
            Decimal(item["price"]) * item["quantity"]
            for item in self.cart.values()
        )

    def clear(self):
        """Vaciar carrito"""
        self.session["cart"] = {}
        self.save()

    def save(self):
        self.session.modified = True