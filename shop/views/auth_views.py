# shop/views/auth_views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect


def custom_signup(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "❌ Please fill all fields")
            return redirect("shop:signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "⚠ Username already exists")
            return redirect("shop:signup")

        user = User.objects.create_user(username=username, password=password)
        login(request, user)

        messages.success(request, "🎉 Account created successfully!")
        return redirect("shop:product_table" if user.is_staff else "shop:products_view")

    return render(request, "shop/signup.html")


def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("shop:product_table" if user.is_staff else "shop:products_view")

        messages.error(request, "❌ Invalid username or password")

    return render(request, "shop/login.html")


def admin_required(view_func):
    """
    Use this decorator to require staff (same behavior as in your original file).
    Keeps code short (wraps user_passes_test).
    """
    return user_passes_test(lambda u: u.is_staff, login_url="shop:login")(view_func)
