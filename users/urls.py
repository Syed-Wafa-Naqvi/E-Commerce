from django.urls import path
from users.views import signup, user_login, dashboard, user_logout, verify_otp, forgot_password, reset_password



urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path("reset-password/", reset_password, name="reset_password"),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', user_logout, name='logout')
]   