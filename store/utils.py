# store/utils.py
from .models import CartItem, Product

def get_cart_items(user):
    return CartItem.objects.filter(user=user)

def get_cart_quantities(cart_items):
    return {item.product.id: item.quantity for item in cart_items}

def is_product_out_of_stock(product, cart_quantity):
    return product.stock == 0 or cart_quantity >= product.stock

def prepare_products_with_status(products, cart_items):
    cart_quantities = get_cart_quantities(cart_items)
    products_with_status = []
    for product in products:
        cart_quantity = cart_quantities.get(product.id, 0)
        is_out_of_stock = is_product_out_of_stock(product, cart_quantity)
        products_with_status.append({'product': product,'is_out_of_stock': is_out_of_stock})
        return products_with_status

def prepare_cart_items_with_status(cart_items):
    cart_items_with_status = []
    for item in cart_items:
        can_increase = item.quantity < item.product.stock
        cart_items_with_status.append({'item': item,'can_increase': can_increase})
    return cart_items_with_status