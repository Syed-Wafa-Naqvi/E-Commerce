from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from django.contrib import messages
from .utils import  prepare_products

def base_page(request):
    return render(request, 'base_page.html')

@login_required
def dashboard(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_items_count = sum(cart.values())
    products_with_status = prepare_products(products, cart)
    return render(request, 'dashboard.html', {'products_with_status': products_with_status,'categories': categories,'category': None,'cart_items_count': cart_items_count})

@login_required
def category_view(request, id):
    category = get_object_or_404(Category, id=id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_items_count = sum(cart.values())
    products_status = prepare_products(products, cart)
    return render(request, 'dashboard.html', {'products_status': products_status,'categories': categories,'category': category,'cart_items_count': cart_items_count})

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_items_count = sum(cart.values())
    cart_quantity = cart.get(str(product_id), 0)
    is_out_of_stock = product.stock == 0 or cart_quantity >= product.stock
    return render(request, 'product_detail.html', {'product': product,'categories': categories,'category': product.category,'cart_items_count': cart_items_count,'is_out_of_stock': is_out_of_stock})

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {}) 
    product = get_object_or_404(Product, id=product_id)
    if str(product_id) in cart:
        if cart[str(product_id)] < product.stock:
            cart[str(product_id)] += 1
            messages.success(request, f"Quantity of {product.name} increased!")
        else:
            messages.error(request, f"Cannot add more {product.name}, stock limit reached!")
    else:
        if product.stock > 0:
            cart[str(product_id)] = 1
            messages.success(request, f"{product.name} added to cart!")
        else:
            messages.error(request, f"{product.name} is out of stock!")
    request.session['cart'] = cart
    return redirect('store:view_cart')

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    categories = Category.objects.all()
    cart_items = []
    total_price = 0
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product_id = str(product_id)
        if product_id in cart:
            product = get_object_or_404(Product, id=product_id)
            if action == 'increase' and cart[product_id] < product.stock:
                cart[product_id] += 1
                messages.success(request, f"Quantity of {product.name} increased!")
            elif action == 'decrease':
                if cart[product_id] > 1:
                    cart[product_id] -= 1
                    messages.success(request, f"Quantity of {product.name} decreased!")
                else:
                    del cart[product_id]
                    messages.success(request, f"{product.name} removed from cart!")
            request.session['cart'] = cart
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total_price += item_total
        can_increase = quantity < product.stock
        cart_items.append({'product': product,'quantity': quantity,'total': item_total,'can_increase': can_increase})

    return render(request, 'cart.html', {'cart_items': cart_items,'categories': categories,'total_price': total_price})

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {}) 
    product_id = str(product_id)
    if product_id in cart:
        product = get_object_or_404(Product, id=product_id)
        del cart[product_id]
        messages.success(request, f"{product.name} removed from cart!")
    request.session['cart'] = cart 
    return redirect('store:view_cart')

@login_required
def clear_cart(request):
    request.session['cart'] = {}  
    messages.success(request, "Your cart has been cleared!")
    return redirect('store:view_cart')

def custom_404(request, exception):
    return render(request, '404.html', status=404)