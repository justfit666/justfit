# shop/views/variant_views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages

from .auth_views import admin_required
from ..models import ProductVariant, Order, OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()


def _to_int(value, default=None):
    try:
        return int(value)
    except Exception:
        return default


@admin_required
def update_variant_field(request, variant_id):
    """
    AJAX endpoint to update specific numeric fields on a ProductVariant.
    Creates an Order when quantity decreases (as per original logic).
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    field = request.POST.get("field")
    value = request.POST.get("value")

    allowed = {"quantity", "availability_count", "in_delivery"}
    if field not in allowed:
        return JsonResponse({"success": False, "message": "Invalid field"}, status=400)

    variant = get_object_or_404(ProductVariant, pk=variant_id)

    ivalue = _to_int(value)
    if ivalue is None or ivalue < 0:
        return JsonResponse({"success": False, "message": "Invalid number"}, status=400)

    old_value = getattr(variant, field, 0)
    new_value = ivalue
    diff = old_value - new_value  # positive => decrease

    if diff > 0:
        # create internal order if decreased
        try:
            admin_user = User.objects.get(username="Justfit")
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "User Justfit not found"}, status=400)

        if field == "in_delivery":
            order_status = "in_progress"
            comment = "Order done by admin (delivery decrease)"
        elif field == "availability_count":
            order_status = "in_progress"
            comment = "Order done by admin (availability decrease)"
        else:
            order_status = "in_progress"
            comment = "Admin update (other decrease)"

        order = Order.objects.create(
            user=admin_user,
            total_price=0,
            status=order_status,
            comment=comment
        )

        OrderItem.objects.create(
            order=order,
            variant=variant,
            quantity=diff,
            price=variant.product.selling_price
        )

    setattr(variant, field, new_value)
    variant.save()

    return JsonResponse({"success": True, "message": "Saved successfully."})


def variant_lookup(request):
    """
    AJAX: find variant by size/color for a product (used in admin quick-add or product page).
    """
    size = request.GET.get("size")
    color = request.GET.get("color")
    product_id = request.GET.get("product_id")

    try:
        variant = ProductVariant.objects.get(product_id=product_id, size=size, color=color)
        data = {
            "id": variant.id,
            "available": variant.is_available() if hasattr(variant, "is_available") else (variant.availability_count > 0),
            "current_quantity": getattr(variant, "current_quantity", variant.quantity),
            "price_after_discount": float(getattr(variant, "price_after_discount", variant.product.selling_price)),
            "selling_price": float(variant.product.selling_price),
            "bought_price": float(getattr(variant, "bought_price", 0)),
        }
        return JsonResponse({"ok": True, "variant": data})
    except ProductVariant.DoesNotExist:
        return JsonResponse({"ok": False, "error": "No variant"})
