# store/urls.py
from django.urls import path
from .views import base_page, dashboard, category_view, product_detail, add_to_cart, view_cart, remove_from_cart, clear_cart,checkout

app_name = 'store'

urlpatterns = [
    path('', base_page, name='base_page'),
    path('dashboard/', dashboard, name='dashboard'),
    path('category/<int:id>/', category_view, name='category_view'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('cart/clear/', clear_cart, name='clear_cart')
]