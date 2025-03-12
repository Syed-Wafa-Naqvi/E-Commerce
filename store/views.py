from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail
from .models import CustomUser
from django.contrib import messages


def signup(request):
    if request.method == 'POST':
        if 'otp' in request.POST:
            email = request.session.get('email')
            otp_entered = request.POST['otp']
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid email.')
                return render(request, 'store/signup.html')
            if user.otp == otp_entered:
                user.is_verified = True
                user.otp = None
                user.save()
                del request.session['email']
                messages.success(request, 'Email verified successfully. You can now log in.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid OTP.')
                return render(request, 'store/signup.html', {'otp_phase': True})

        else:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

            if not username or not email or not password:
                messages.error(request, 'All fields are required.')
                return render(request, 'store/signup.html')

            user = CustomUser.objects.filter(email=email).first()

            if user:
                if not user.is_verified:
                    user.generate_otp()
                    send_mail('Your OTP for Verification',f'Your OTP is {user.otp}','your-email@gmail.com',[email],fail_silently=False,)
                    request.session['email'] = email
                    messages.info(request, 'OTP resent. Please check your email.')
                    return render(request, 'store/signup.html', {'otp_phase': True})
                
                messages.error(request, 'Email already registered.')
                return render(request, 'store/signup.html')

            user = CustomUser.objects.create_user(username=username, email=email, password=password, is_verified=False)
            user.generate_otp()
            send_mail('Your OTP for Verification',f'Your OTP is {user.otp}','your-email@gmail.com',[email],fail_silently=False)
            request.session['email'] = email  
            messages.success(request, 'OTP sent to your email. Please verify.')
            return render(request, 'store/signup.html', {'otp_phase': True})  
    return render(request, 'store/signup.html')
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, 'Both username and password are required.')
            return render(request, 'store/login.html')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_verified:
                login(request, user)
                messages.success(request, 'Logged in successfully.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Please verify your email with OTP first.')
                return render(request, 'store/login.html')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'store/login.html')

    return render(request, 'store/login.html')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'store/dashboard.html', {'message': 'Welcome to the dashboard'})


def user_logout(request):
    logout(request)
    return redirect('login')