# users/urls.py
from django.urls import path
from .views import signup, verify_otp, forgot_password, reset_password, user_login, user_logout, change_username, change_password
app_name = 'users'

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('change-username/', change_username, name='change_username'),
    path('change-password/', change_password, name='change_password'),
]