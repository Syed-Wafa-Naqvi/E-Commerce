def get_cart_quantities(cart):
    return {int(product_id): quantity for product_id, quantity in cart.items()}

def prepare_products(products, cart):
    cart_quantities = get_cart_quantities(cart)
    products_with_status = []
    for product in products:
        quantity_in_cart = cart_quantities.get(product.id, 0)
        is_out_of_stock = product.stock == 0 or quantity_in_cart >= product.stock
        products_with_status.append({
            'product': product,
            'quantity_in_cart': quantity_in_cart,
            'is_out_of_stock': is_out_of_stock,
        })
    return products_with_status