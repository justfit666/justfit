# shop/views/favorite_cart_views.py
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from ..models import ProductVariant, CartItem, Product, Favorite


@login_required
def add_to_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    cart = request.session.get("cart", {})
    cart_key = str(variant_id)
    cart[cart_key] = cart.get(cart_key, 0) + 1
    request.session["cart"] = cart
    return JsonResponse({"status": "success", "message": "Added to cart"})


@login_required
def toggle_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart_item = CartItem.objects.filter(user=request.user, variant=variant).first()
    if cart_item:
        cart_item.delete()
    else:
        CartItem.objects.create(user=request.user, variant=variant)
    return redirect("shop:product_detail", product_id=variant.product.id)


@login_required
def add_to_favorite(request, product_id):
    # session-based favorite add (keeps original minimal approach)
    _ = get_object_or_404(Product, pk=product_id)
    fav = request.session.get("favorites", [])
    if product_id not in fav:
        fav.append(product_id)
    request.session["favorites"] = fav
    return JsonResponse({"status": "success", "message": "Added to favorites"})


@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
    return redirect(request.META.get("HTTP_REFERER", "shop:product_list"))
