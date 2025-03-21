from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Category, CartItem
from django.contrib import messages
from .utils import get_cart_items, prepare_products_with_status, prepare_cart_items_with_status

def base_page(request):
    return render(request, 'base_page.html')

@login_required
def dashboard(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    cart_items = get_cart_items(request.user)
    products_with_status = prepare_products_with_status(products, cart_items)
    return render(request, 'dashboard.html', {'products_with_status': products_with_status,'categories': categories,'category': None,'cart_items': cart_items})

@login_required
def category_view(request, id):
    category = get_object_or_404(Category, id=id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    cart_items = get_cart_items(request.user)
    products_with_status = prepare_products_with_status(products, cart_items)
    return render(request, 'dashboard.html', {'products_with_status': products_with_status,'categories': categories,'category': category,'cart_items': cart_items})

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    cart_items = get_cart_items(request.user)
    cart_item = cart_items.filter(product=product).first()
    cart_quantity = cart_item.quantity if cart_item else 0
    is_out_of_stock = product.stock == 0 or cart_quantity >= product.stock
    return render(request, 'product_detail.html', {'product': product,'categories': categories,'category': product.category,'cart_items': cart_items,'is_out_of_stock': is_out_of_stock})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
    available_stock = product.stock - cart_item.quantity
    if available_stock <= 0:
        messages.error(request, f"{product.name} is out of stock!")
        return redirect('store:dashboard')
    cart_item.quantity += 1
    if cart_item.quantity > product.stock:
        messages.error(request, f"Cannot add more {product.name} to cart. Only {product.stock} items available!")
        return redirect('store:dashboard')
    cart_item.save()
    messages.success(request, f"{product.name} has been added to your cart!")
    return redirect('store:view_cart')

@login_required
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if cart_item.quantity >= cart_item.product.stock:
        messages.error(request, f"Item is out of stock!")  # Prompt message when stock limit is reached
        return redirect('store:view_cart')
    cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f"Quantity of {cart_item.product.name} increased!")
    return redirect('store:view_cart')

@login_required
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, f"Quantity of {cart_item.product.name} decreased!")
    else:
        cart_item.delete()
        messages.success(request, f"{cart_item.product.name} removed from your cart!")
    return redirect('store:view_cart')

@login_required
def view_cart(request):
    cart_items = get_cart_items(request.user)
    categories = Category.objects.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart_items_with_status = prepare_cart_items_with_status(cart_items)
    return render(request, 'cart.html', {'cart_items_with_status': cart_items_with_status,'categories': categories,'total_price': total_price})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from your cart!")
    return redirect('store:view_cart')

@login_required
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, "Your cart has been cleared!")
    return redirect('store:view_cart')

def custom_404(request, exception):
    return render(request, '404.html', status=404)