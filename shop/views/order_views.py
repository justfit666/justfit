# shop/views/order_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Prefetch
from django.contrib import messages

from .auth_views import admin_required
from ..models import Order, OrderItem


@admin_required
def admin_order_list(request):
    status_filter = request.GET.get("status")
    orders = Order.objects.prefetch_related(Prefetch("items"), "user").order_by("-created_at")
    if status_filter:
        orders = orders.filter(status=status_filter)
    else:
        status_filter = "in_progress"
        orders = orders.filter(status="in_progress")

    return render(request, "shop/admin_order_list.html", {
        "orders": orders,
        "status_filter": status_filter,
        "status_choices": Order.STATUS_CHOICES,
    })


@admin_required
def bulk_update_orders(request):
    if request.method != "POST":
        return redirect("shop:admin_order_list")

    order_ids = request.POST.getlist("order_ids")
    new_status = request.POST.get("new_status")
    if not order_ids:
        messages.error(request, "No orders selected.")
        return redirect("shop:admin_order_list")
    if not new_status:
        messages.error(request, "You must select a new status.")
        return redirect("shop:admin_order_list")

    orders = Order.objects.filter(id__in=order_ids)

    if new_status == "cancelled":
        for order in orders:
            for item in order.items.all():
                if item.variant:
                    item.variant.availability_count += item.quantity
                    item.variant.save()

    orders.update(status=new_status)
    messages.success(request, f"Updated {len(order_ids)} orders to '{new_status}'.")
    return redirect("shop:admin_order_list")


@admin_required
def update_order_status(request, order_id):
    if request.method == "POST":
        new_status = request.POST.get("status")
        order = get_object_or_404(Order, id=order_id)

        if new_status == "cancelled":
            for item in order.items.all():
                if item.variant:
                    item.variant.availability_count += item.quantity
                    item.variant.save()

        order.status = new_status
        order.save()
        return JsonResponse({"success": True, "new_status": new_status})

    return JsonResponse({"success": False})


@admin_required
def update_item_status(request, item_id):
    if request.method == "POST":
        new_status = request.POST.get("status")
        item = get_object_or_404(OrderItem, id=item_id)
        item.status = new_status
        item.save()
        return JsonResponse({"success": True, "new_status": new_status})
    return JsonResponse({"success": False})


@admin_required
def ajax_update_order_field(request, order_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"})

    field = request.POST.get("field")
    value = request.POST.get("value")
    if not field:
        return JsonResponse({"success": False, "message": "Field is missing"})

    order = get_object_or_404(Order, id=order_id)
    if field not in ["cutomer_name", "comment","price"]:
        return JsonResponse({"success": False, "message": "Invalid field"})

    setattr(order, field, value)
    order.save()
    return JsonResponse({"success": True})


@admin_required
def ajax_update_item_field(request, item_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    field = request.POST.get("field")
    value = request.POST.get("value")

    item = get_object_or_404(OrderItem, id=item_id)

    if field not in ["price"]:
        return JsonResponse({"success": False, "message": "Invalid field"})

    try:
        value = float(value)
    except:
        return JsonResponse({"success": False, "message": "Invalid number"})

    setattr(item, field, value)
    item.save()

    return JsonResponse({"success": True})

