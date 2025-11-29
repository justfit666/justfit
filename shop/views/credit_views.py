# shop/views/credit_views.py
from django.shortcuts import render, redirect, get_object_or_404
from .auth_views import admin_required
from ..models import Credit, User
from django.db.models import Sum



@admin_required
def add_credit(request):
    admin_users = User.objects.filter(is_staff=True)
    if request.method == "POST":
        amount = request.POST.get("amount")
        comment = request.POST.get("comment")
        user_id = request.POST.get("user")
        Credit.objects.create(user_id=user_id, amount=amount, comment=comment)
        return redirect("shop:credit_list")
    return render(request, "shop/add_credit.html", {"admin_users": admin_users})


@admin_required
def credit_list(request):
    credits = Credit.objects.all().order_by("-date")
    return render(request, "shop/credit_list.html", {"credits": credits})


@admin_required
def balance_credit(request):
    credit_totals = Credit.objects.values("user__username").annotate(total=Sum("amount")).order_by("user__username")
    credits = Credit.objects.exclude(user__username="Justfit").order_by("-date")
    admin_users = User.objects.filter(is_staff=True)
    return render(request, "shop/balance_credit.html", {
        "credit_totals": credit_totals,
        "credits": credits,
        "admin_users": admin_users
    })


@admin_required
def update_credit_user(request, pk):
    credit = get_object_or_404(Credit, pk=pk)
    new_user_id = request.POST.get("user")
    if new_user_id:
        credit.user_id = new_user_id
        credit.save()
    return redirect("shop:balance_credit")
