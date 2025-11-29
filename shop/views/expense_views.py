# shop/views/expense_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import F, Sum, ExpressionWrapper, DecimalField

from .auth_views import admin_required
from ..models import Expense, User, ProductVariant


@admin_required
def add_expense(request):
    admin_users = User.objects.filter(is_staff=True)
    if request.method == "POST":
        amount = request.POST.get("amount")
        comment = request.POST.get("comment")
        type_ = request.POST.get("type")
        user_id = request.POST.get("user")
        Expense.objects.create(user_id=user_id, amount=amount, comment=comment, type=type_)
        return redirect("shop:expense_list")
    return render(request, "shop/add_expense.html", {"admin_users": admin_users})


@admin_required
def expense_list(request):
    expenses = Expense.objects.all().order_by("-date")
    return render(request, "shop/expense_list.html", {"expenses": expenses})


@admin_required
def profit_report(request):
    # profit estimate using variant sold units formula you used
    product_profit = ProductVariant.objects.annotate(
        sold_units=F("quantity") - F("availability_count") - F("in_delivery"),
        revenue=ExpressionWrapper(
            F("sold_units") * (F("product__selling_price") - F("product__purchase_price") - 20),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    ).aggregate(total_profit=Sum("revenue"))["total_profit"] or 0

    expense_out = Expense.objects.filter(type__in=["Extra offer", "Ads", "Other"]).aggregate(total_out=Sum("amount"))["total_out"] or 0
    expense_in = Expense.objects.filter(type="Extra gain").aggregate(total_in=Sum("amount"))["total_in"] or 0
    final_profit = product_profit - expense_out + expense_in

    return render(request, "shop/profit_report.html", {
        "profit": final_profit,
        "product_profit": product_profit,
        "expense_out": expense_out,
        "expense_in": expense_in,
    })


@admin_required
def balance(request):
    user_totals = Expense.objects.values("user__username").annotate(total=Sum("amount")).order_by("user__username")
    expenses = Expense.objects.exclude(user__username="Justfit").order_by("-date")
    admin_users = User.objects.filter(is_staff=True)
    return render(request, "shop/balance.html", {
        "user_totals": user_totals,
        "expenses": expenses,
        "admin_users": admin_users
    })


@admin_required
def update_expense_user(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    new_user_id = request.POST.get("user")
    if new_user_id:
        expense.user_id = new_user_id
        expense.save()
    return redirect("shop:balance")
