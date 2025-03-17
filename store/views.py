from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.conf import settings
from django.utils.timezone import now, timedelta
from .models import CustomUser
from .forms import SignUpForm
import random

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            username = form.cleaned_data["username"]
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email already exists! Please use a different email.")
                return redirect("signup")
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Username already exists! Please choose a different username.")
                return redirect("signup")
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.otp = str(random.randint(100000, 999999))
            user.otp_created_at = now()
            user.is_verified = False
            user.save()
            send_mail(subject="Your OTP for Email Verification",message=f"Your OTP is {user.otp}. Please verify your email within 10 minutes.",from_email=settings.EMAIL_HOST_USER,recipient_list=[user.email],fail_silently=False)
            request.session["email"] = user.email
            messages.success(request, "OTP sent to your email! Please verify within 10 minutes.")
            return redirect("verify_otp")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def verify_otp(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "Session expired! Please try again")
        return redirect("signup")  
    if request.method == "POST":
        otp = request.POST.get("otp")
        user = CustomUser.objects.filter(email=email, otp=otp).first()
        if user:
            if now() - user.otp_created_at > timedelta(minutes=10):
                messages.error(request, "OTP expired! Please request a new one.")
                return redirect("forgot_password" if "forgot_password_flow" in request.session else "signup")
            user.is_verified = True
            user.otp = None
            user.otp_created_at = None
            user.save()
            if request.session.get("forgot_password_flow"):
                request.session["otp_verified"] = True  
                del request.session["forgot_password_flow"]
                messages.success(request, "OTP verified successfully! You can now reset your password.")
                return redirect("reset_password")

            messages.success(request, "Email verified successfully! You can now log in.")
            return redirect("login")

        else:
            messages.error(request, "Invalid OTP! Please try again")

    return render(request, "verify_otp.html")



def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, "User with this email does not exist")
            return redirect("forgot_password")
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_created_at = now()
        user.save()
        send_mail(subject="Password Reset OTP",message=f"Your OTP for password reset is {otp}. It will expire in 10 minutes.",from_email=settings.EMAIL_HOST_USER,recipient_list=[email],fail_silently=False)
        request.session["email"] = email
        request.session["forgot_password_flow"] = True
        messages.success(request, "OTP has been sent to your email")
        return redirect("verify_otp")
    return render(request, "forgot_password.html")



def reset_password(request):
    email = request.session.get("email")
    otp_verified = request.session.get("otp_verified")
    if not email or not otp_verified:
        messages.error(request, "Unauthorized access! Please verify OTP first")
        return redirect("forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match! Please try again")
            return redirect("reset_password")

        user = CustomUser.objects.filter(email=email).first()
        if user:
            user.password = make_password(new_password)
            user.otp = None
            user.otp_created_at = None
            user.save()
            del request.session["email"]
            del request.session["otp_verified"]

            messages.success(request, "Password has been reset successfully. You can now log in.")
            return redirect("login")

    return render(request, "reset_password.html")



def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username") 
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_verified:
                messages.error(request, "Please verify your email first.")
                return redirect("login")

            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, "login.html")


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "dashboard.html", {"message": "Welcome to your Dashboard!"})


def user_logout(request):
    logout(request)
    return redirect("login")
