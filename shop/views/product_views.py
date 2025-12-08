# shop/views/product_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Prefetch
from django.views.decorators.http import require_POST

from .auth_views import admin_required
from ..models import (
    Product, ProductVariant, ProductImage, SizeType,
    Category, SubCategory, Favorite
)


@admin_required
def product_table(request):
    products_qs = Product.objects.prefetch_related(
        Prefetch("variants"),
        Prefetch("images")
    ).all()

    # filters
    search = request.GET.get("search", "").strip()
    if search:
        products_qs = products_qs.filter(name__icontains=search)

    category_id = request.GET.get("category")
    if category_id:
        products_qs = products_qs.filter(category_id=category_id)

    colors = request.GET.getlist("color")
    if colors:
        products_qs = products_qs.filter(variants__color__in=colors).distinct()

    sizes = request.GET.getlist("size")
    if sizes:
        products_qs = products_qs.filter(variants__size__in=sizes).distinct()

    availability = request.GET.get("availability")
    if availability == "in_stock":
        products_qs = products_qs.filter(variants__availability_count__gt=0).distinct()
    elif availability == "out_of_stock":
        products_qs = products_qs.filter(variants__availability_count=0).distinct()

    # in_delivery = request.GET.get("in_delivery")
    # if in_delivery == "yes":
    #     products_qs = products_qs.filter(variants__in_delivery__gt=0).distinct()
    # elif in_delivery == "no":
    #     products_qs = products_qs.filter(variants__in_delivery=0).distinct()

    min_qty = request.GET.get("min_qty")
    max_qty = request.GET.get("max_qty")
    if min_qty:
        products_qs = products_qs.filter(variants__availability_count__gte=min_qty).distinct()
    if max_qty:
        products_qs = products_qs.filter(variants__availability_count__lte=max_qty).distinct()

    # sort
    sort = request.GET.get("sort")
    products = list(products_qs)  # evaluate
    if sort == "qty_high":
        products.sort(key=lambda p: getattr(p, "total_quantity", 0), reverse=True)
    elif sort == "qty_low":
        products.sort(key=lambda p: getattr(p, "total_quantity", 0))
    elif sort == "name_az":
        products = sorted(products, key=lambda p: p.name.lower())
    elif sort == "name_za":
        products = sorted(products, key=lambda p: p.name.lower(), reverse=True)

    all_colors = ProductVariant.objects.values_list("color", flat=True).distinct()
    all_sizes = ProductVariant.objects.values_list("size", flat=True).distinct()
    categories = Category.objects.all()

    return render(request, "shop/product_table.html", {
        "products": products,
        "categories": categories,
        "colors": all_colors,
        "sizes": all_sizes,
        "selected_colors": colors,
        "selected_sizes": sizes,
        "search": search,
        "selected_category": category_id,
        "sort": sort,
        "availability": availability,
        "min_qty": min_qty,
        "max_qty": max_qty,
        # "in_delivery_filter": in_delivery,
    })


def products_view(request):
    """
    Public products view (placeholder). Expand with pagination/filters as needed.
    """
    return render(request, "shop/products_view.html", {})


def product_list(request):
    products = Product.objects.all()
    for p in products:
        try:
            p.original_price = p.selling_price + (p.selling_price * (p.discount / 100))
        except Exception:
            p.original_price = p.selling_price

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(request.user.favorites.values_list("product_id", flat=True))

    return render(request, "shop/product_list.html", {
        "products": products,
        "favorite_ids": favorite_ids,
    })


def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        product.original_price = product.selling_price + (product.selling_price * (product.discount / 100))
    except Exception:
        product.original_price = product.selling_price
    variants = product.variants.filter(availability_count__gt=0)
    sizes = variants.values_list("size", flat=True).distinct()
    colors = variants.values_list("color", flat=True).distinct()
    current_variant = variants.first()

    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, product=product).exists()

    return render(request, "shop/product_detail.html", {
        "product": product,
        "variants": variants,
        "current_variant": current_variant,
        "sizes": sizes,
        "colors": colors,
        "is_favorite": is_favorite
    })


@admin_required
def fast_add_product(request):
    """
    Admin quick product add. Supports variants and images like original file.
    Keeps previous behavior: on POST creates product, variants, and images.
    """
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    size_types = SizeType.objects.all()

    previous_data = request.POST.dict() if request.method == "POST" else {}

    if request.method == "POST":
        try:
            name = request.POST.get("name")
            category_id = request.POST.get("category")
            subcategory_id = request.POST.get("subcategory")
            size_type_id = request.POST.get("size_type")
            purchase_price = request.POST.get("purchase_price") or 0
            selling_price = request.POST.get("selling_price") or 0
            discount = request.POST.get("discount") or 0
            description = request.POST.get("description")

            category = Category.objects.filter(id=category_id).first() if category_id else None
            subcategory = SubCategory.objects.filter(id=subcategory_id).first() if subcategory_id else None
            size_type = SizeType.objects.filter(id=size_type_id).first() if size_type_id else None

            product = Product.objects.create(
                name=name,
                category=category,
                subcategory=subcategory,
                size_type=size_type,
                purchase_price=purchase_price,
                selling_price=selling_price,
                discount=discount,
                description=description
            )

            # Variants arrays: sizes/colors/quantities
            sizes_list = request.POST.getlist("variant_size[]")
            colors_list = request.POST.getlist("variant_color[]")
            quantities = request.POST.getlist("variant_quantity[]")
            for i in range(len(sizes_list)):
                s = sizes_list[i]
                c = colors_list[i] if i < len(colors_list) else ""
                q = int(quantities[i] or 0) if i < len(quantities) else 0
                if s and c:
                    ProductVariant.objects.create(
                        product=product,
                        size=s,
                        color=c,
                        quantity=q,
                        availability_count=q
                    )

            # Images
            for f in request.FILES.getlist("images"):
                ProductImage.objects.create(product=product, image=f)

            messages.success(request, f"✅ Product '{product.name}' added successfully!")
            return redirect("shop:fast_add_product")

        except Exception as e:
            messages.error(request, f"❌ Error adding product: {str(e)}")

    return render(request, "shop/fast_add_product.html", {
        "categories": categories,
        "subcategories": subcategories,
        "size_types": size_types,
        "previous_data": previous_data
    })


def get_filtered_variant(request, product_id):
    """
    Returns sizes/colors available for a product after applying selected filters.
    Mirrors original behavior to be used by frontend AJAX.
    """
    size = request.GET.get("size")
    color = request.GET.get("color")
    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.filter(availability_count__gt=0)

    if size:
        variants = variants.filter(size=size)
    if color:
        variants = variants.filter(color=color)

    sizes = variants.values_list("size", flat=True).distinct()
    colors = variants.values_list("color", flat=True).distinct()
    variant = variants.first()

    return JsonResponse({
        "sizes": list(sizes),
        "colors": list(colors),
        "variant_id": variant.id if variant else None,
    })


# Optional: small helper - variant lookup moved to variant_views.py in the reorg,
# but we keep a thin helper here only if templates call views.variant_lookup directly.
def variant_lookup(request):
    size = request.GET.get("size")
    color = request.GET.get("color")
    product_id = request.GET.get("product_id")
    try:
        variant = ProductVariant.objects.get(product_id=product_id, size=size, color=color)
        data = {
            "id": variant.id,
            "available": variant.availability_count > 0,
            "current_quantity": getattr(variant, "current_quantity", variant.quantity),
            "price_after_discount": float(getattr(variant, "price_after_discount", variant.product.selling_price)),
            "selling_price": float(variant.product.selling_price),
            "bought_price": float(getattr(variant, "bought_price", 0)),
        }
        return JsonResponse({"ok": True, "variant": data})
    except ProductVariant.DoesNotExist:
        return JsonResponse({"ok": False, "error": "No variant"})
