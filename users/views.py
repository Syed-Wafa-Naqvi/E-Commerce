# users/views.py
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.conf import settings
from django.utils.timezone import now, timedelta
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .forms import SignUpForm
from store.models import Category, CartItem
import random

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            username = form.cleaned_data["username"]
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email already exists! Please use a different email.")
                return redirect("users:signup")
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Username already exists! Please choose a different username.")
                return redirect("users:signup")
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.otp = str(random.randint(100000, 999999))
            user.otp_created_at = now()
            user.is_verified = False
            user.save()
            send_mail(subject="Your OTP for Email Verification", message=f"Your OTP is {user.otp}. Please verify your email within 10 minutes.", from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email], fail_silently=False)
            request.session["email"] = user.email
            messages.success(request, "OTP sent to your email! Please verify within 10 minutes.")
            return redirect("users:verify_otp")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

def verify_otp(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "Session expired! Please try again")
        return redirect("users:signup")  
    if request.method == "POST":
        otp = request.POST.get("otp")
        user = CustomUser.objects.filter(email=email, otp=otp).first()
        if user:
            if now() - user.otp_created_at > timedelta(minutes=10):
                messages.error(request, "OTP expired! Please request a new one.")
                return redirect("users:forgot_password" if "forgot_password_flow" in request.session else "users:signup")
            user.is_verified = True
            user.otp = None
            user.otp_created_at = None
            user.save()
            if request.session.get("forgot_password_flow"):
                request.session["otp_verified"] = True  
                del request.session["forgot_password_flow"]
                messages.success(request, "OTP verified successfully! You can now reset your password.")
                return redirect("users:reset_password")
            messages.success(request, "Email verified successfully! You can now log in.")
            return redirect("users:login")
        else:
            messages.error(request, "Invalid OTP! Please try again")
    return render(request, "verify_otp.html")

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, "User with this email does not exist")
            return redirect("users:forgot_password")
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_created_at = now()
        user.save()
        send_mail(subject="Password Reset OTP", message=f"Your OTP for password reset is {otp}. It will expire in 10 minutes.", from_email=settings.EMAIL_HOST_USER, recipient_list=[email], fail_silently=False)
        request.session["email"] = email
        request.session["forgot_password_flow"] = True
        messages.success(request, "OTP has been sent to your email")
        return redirect("users:verify_otp")
    return render(request, "forgot_password.html")

def reset_password(request):
    categories = Category.objects.all()
    cart_items = CartItem.objects.filter(user=request.user) if request.user.is_authenticated else []
    if request.method == "POST":
        if request.user.is_authenticated:
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match! Please try again")
                return redirect("users:reset_password")
            user = request.user
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password has been changed successfully. Please log in again.")
            logout(request)
            return redirect("users:login")
        else:
            email = request.session.get("email")
            otp_verified = request.session.get("otp_verified")
            if not email or not otp_verified:
                messages.error(request, "Unauthorized access! Please verify OTP first")
                return redirect("users:forgot_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match! Please try again")
                return redirect("users:reset_password")
            user = CustomUser.objects.filter(email=email).first()
            if user:
                user.password = make_password(new_password)
                user.otp = None
                user.otp_created_at = None
                user.save()
                del request.session["email"]
                del request.session["otp_verified"]
                messages.success(request, "Password has been reset successfully. You can now log in.")
                return redirect("users:login")
    return render(request, "reset_password.html", {"categories": categories,"cart_items": cart_items})

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username") 
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_verified:
                messages.error(request, "Please verify your email first.")
                return redirect("users:login")
            login(request, user)
            return redirect("store:dashboard")
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    messages.success(request, "Logout successful!")
    return redirect("users:login")

@login_required
def change_username(request):
    categories = Category.objects.all()
    cart_items = CartItem.objects.filter(user=request.user)
    if request.method == "POST":
        new_username = request.POST.get("new_username")
        if not new_username:
            messages.error(request, "Please provide a new username.")
            return redirect("users:change_username")
        if CustomUser.objects.filter(username=new_username).exclude(id=request.user.id).exists():
            messages.error(request, "This username is already taken. Please choose a different one.")
            return redirect("users:change_username")
        user = request.user
        user.username = new_username
        user.save()
        messages.success(request, "Username changed successfully!")
        return redirect("store:dashboard")
    return render(request, "change_username.html", {"categories": categories,"cart_items": cart_items})

@login_required
def change_password(request):
    request.session["email"] = request.user.email
    return redirect("users:reset_password")