from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Category,OrderShipment
from django.contrib import messages
from .utils import  prepare_products
from .forms import CheckoutForm

def base_page(request):
    return render(request, 'base_page.html')

@login_required
def dashboard(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_items_count = len(cart)
    products_with_status = prepare_products(products, cart)
    return render(request, 'dashboard.html', {'products_with_status': products_with_status,'categories': categories,'category': None,'cart_items_count': cart_items_count})

@login_required
def category_view(request, id):
    category = get_object_or_404(Category, id=id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_items_count = sum(cart.values())
    products_with_status = prepare_products(products, cart)
    return render(request, 'dashboard.html', {'products_with_status': products_with_status,'categories': categories,'category': category,'cart_items_count': cart_items_count})

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

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty!")
        return redirect('store:view_cart')
    cart_items = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({'product': product, 'quantity': quantity, 'total': item_total})
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            phone = form.cleaned_data['phone']
            order = OrderShipment.objects.create(address=address, phone=phone, user=request.user)
            ordered_items = []
            order_items = []
            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, id=product_id)
                if product.stock >= quantity:
                    product.stock -= quantity
                    product.save()
                    item_total = float(product.price * quantity)
                    order_items.append({'product': product.name, 'quantity': quantity, 'total': item_total})
                    ordered_items.append({'product': product, 'quantity': quantity, 'total': product.price * quantity})
                else:
                    messages.error(request, f"Insufficient stock for {product.name}. Order not placed.")
                    return redirect('store:view_cart')
            order.items = order_items
            order.shipping_address = address
            order.save()
            request.session['cart'] = {}  
            messages.success(request, "Order placed successfully!")
            return render(request, 'thank_you.html', {'ordered_items': ordered_items})
    else:
        form = CheckoutForm()

    categories = Category.objects.all()
    return render(request, 'checkout.html', {'form': form,'cart_items': cart_items,'total_price': total_price,'categories': categories})

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            total = float(product.price) * quantity 
            cart_items.append({
                'product': {'id': product.id,'name': product.name,'price': float(product.price)},'quantity': quantity,'total': total})
            total_price += total
        except Product.DoesNotExist:
            continue
    categories = Category.objects.all()
    cart_items_count = sum(cart.values())
    if not cart_items:
        messages.error(request, "Your cart is empty. Please add items to your cart before checking out.")
        return redirect('store:view_cart')
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order_shipment = OrderShipment.objects.create(user=request.user,address=form.cleaned_data['address'],phone=form.cleaned_data['phone'],items=cart_items )
            request.session['cart'] = {}
            request.session.modified = True
            return render(request, 'thank_you.html', {'ordered_items': cart_items,'total_price': total_price,'address': form.cleaned_data['address'],'phone': form.cleaned_data['phone'],'categories': categories,'cart_items_count': 0 })
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = CheckoutForm()
    return render(request, 'checkout.html', {'cart_items': cart_items,'total_price': total_price,'form': form,'categories': categories,'cart_items_count': cart_items_count})