# shop/views.py


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, ProductVariant, ProductImage, SizeType, Category, SubCategory,Favorite,CartItem,Credit
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model

def custom_signup(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        password = request.POST.get("password")

        # Minimal validation
        if not username or not password:
            messages.error(request, "❌ Please fill all fields")
            return redirect("shop:signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "⚠ Username already exists")
            return redirect("shop:signup")

        # Create user (normal user by default)
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # Auto-login
        login(request, user)

        messages.success(request, "🎉 Account created successfully!")

        # Staff go to product table
        if user.is_staff:
            return redirect("shop:product_table")

        # Normal users go to main products page
        return redirect("shop:products_view")

    return render(request, "shop/signup.html")


def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect staff
            if user.is_staff:
                return redirect("shop:product_table")

            # Redirect normal users somewhere else (products page)
            return redirect("shop:products_view")

        else:
            messages.error(request, "❌ Invalid username or password")

    return render(request, "shop/login.html")
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url="shop:login")(view_func)


@admin_required
def product_table(request):
    products = Product.objects.prefetch_related('variants', 'images').all()

    # --- 🔍 SEARCH ---
    search = request.GET.get("search", "")
    if search:
        products = products.filter(name__icontains=search)

    # --- 🗂 CATEGORY FILTER ---
    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    # --- 🎨 MULTI-COLOR FILTER ---
    colors = request.GET.getlist("color")
    if colors:
        products = products.filter(variants__color__in=colors).distinct()

    # --- 📏 MULTI-SIZE FILTER ---
    sizes = request.GET.getlist("size")
    if sizes:
        products = products.filter(variants__size__in=sizes).distinct()

    # --- 📦 AVAILABILITY FILTER ---
    availability = request.GET.get("availability")
    if availability == "in_stock":
        products = products.filter(variants__availability_count__gt=0).distinct()
    elif availability == "out_of_stock":
        products = products.filter(variants__availability_count=0).distinct()

    # --- 🚚 IN DELIVERY FILTER ---
    in_delivery_filter = request.GET.get("in_delivery")
    if in_delivery_filter == "yes":
        products = products.filter(variants__in_delivery__gt=0).distinct()
    elif in_delivery_filter == "no":
        products = products.filter(variants__in_delivery=0).distinct()

    # --- RANGE FILTER ---
    min_qty = request.GET.get("min_qty")
    max_qty = request.GET.get("max_qty")
    if min_qty:
        products = products.filter(variants__availability_count__gte=min_qty).distinct()
    if max_qty:
        products = products.filter(variants__availability_count__lte=max_qty).distinct()

    # --- 🔃 SORT ---
    sort = request.GET.get("sort")
    if sort == "qty_high":
        products = sorted(products, key=lambda p: p.total_quantity, reverse=True)
    elif sort == "qty_low":
        products = sorted(products, key=lambda p: p.total_quantity)
    elif sort == "name_az":
        products = products.order_by("name")
    elif sort == "name_za":
        products = products.order_by("-name")

    # Distinct values
    all_colors = ProductVariant.objects.values_list("color", flat=True).distinct()
    all_sizes = ProductVariant.objects.values_list("size", flat=True).distinct()
    categories = Category.objects.all()

    return render(request, 'shop/product_table.html', {
        'products': products,
        'categories': categories,
        'colors': all_colors,
        'sizes': all_sizes,
        'selected_colors': colors,
        'selected_sizes': sizes,
        'search': search,
        'selected_category': category_id,
        'sort': sort,
        'availability': availability,
        'min_qty': min_qty,
        'max_qty': max_qty,
        'in_delivery_filter': in_delivery_filter,  # NEW
    })

# @admin_required
# def product_table(request):
#     products = Product.objects.prefetch_related('variants', 'images').all()

#     # --- 🔍 SEARCH ---
#     search = request.GET.get("search", "")
#     if search:
#         products = products.filter(name__icontains=search)

#     # --- 🗂 CATEGORY FILTER ---
#     category_id = request.GET.get("category")
#     if category_id:
#         products = products.filter(category_id=category_id)

#     # --- 🎨 MULTI-COLOR FILTER ---
#     colors = request.GET.getlist("color")
#     if colors:
#         products = products.filter(variants__color__in=colors).distinct()

#     # --- 📏 MULTI-SIZE FILTER ---
#     sizes = request.GET.getlist("size")
#     if sizes:
#         products = products.filter(variants__size__in=sizes).distinct()

#     # --- 📦 AVAILABILITY FILTER ---
#     availability = request.GET.get("availability")
    

#     if availability == "in_stock":
#         products = products.filter(variants__availability_count__gt=0).distinct()

#     elif availability == "out_of_stock":
#         products = products.filter(variants__availability_count=0).distinct()

#     # Range filter (optional)
#     min_qty = request.GET.get("min_qty")
#     max_qty = request.GET.get("max_qty")

#     if min_qty:
#         products = products.filter(variants__availability_count__gte=min_qty).distinct()
#     if max_qty:
#         products = products.filter(variants__availability_count__lte=max_qty).distinct()

#     # --- 🔃 SORT ---
#     sort = request.GET.get("sort")
#     if sort == "qty_high":
#         products = sorted(products, key=lambda p: p.total_quantity, reverse=True)
#     elif sort == "qty_low":
#         products = sorted(products, key=lambda p: p.total_quantity)
#     elif sort == "name_az":
#         products = products.order_by("name")
#     elif sort == "name_za":
#         products = products.order_by("-name")

#     # Distinct color/size values from all variants
#     all_colors = ProductVariant.objects.values_list("color", flat=True).distinct()
#     all_sizes = ProductVariant.objects.values_list("size", flat=True).distinct()

#     categories = Category.objects.all()

#     return render(request, 'shop/product_table.html', {
#         'products': products,
#         'categories': categories,

#         'colors': all_colors,
#         'sizes': all_sizes,

#         'selected_colors': colors,
#         'selected_sizes': sizes,

#         'search': search,
#         'selected_category': category_id,
#         'sort': sort,

#         'availability': availability,
#         'min_qty': min_qty,
#         'max_qty': max_qty,
#     })


@require_POST
def update_variant_field(request, variant_id):
    """
    Update a single variant field:
    - quantity
    - availability_count
    - in_delivery
    Returns JSON: { success: bool, message: str }
    """

    field = request.POST.get("field")
    value = request.POST.get("value")

    # Add in_delivery to allowed fields
    allowed = {"quantity", "availability_count", "in_delivery"}
    
    if field not in allowed:
        return JsonResponse({"success": False, "message": "Invalid field."}, status=400)

    try:
        variant = get_object_or_404(ProductVariant, pk=variant_id)
    except Exception:
        return JsonResponse({"success": False, "message": "Variant not found."}, status=404)

    try:
        # All 3 fields must be positive integers
        ivalue = int(value)
        if ivalue < 0:
            return JsonResponse({"success": False, "message": "Value must be zero or positive."}, status=400)

        # Update the field
        setattr(variant, field, ivalue)
        variant.save()

        return JsonResponse({"success": True, "message": "Saved successfully."})

    except ValueError:
        return JsonResponse({"success": False, "message": "Please enter a valid integer."}, status=400)

    except Exception as e:
        return JsonResponse({"success": False, "message": f"Server error: {str(e)}"}, status=500)

###############################
@admin_required
def fast_add_product(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    size_types = SizeType.objects.all()

    # Pre-fill form values if error occurs
    previous_data = request.POST.dict() if request.method == "POST" else {}

    if request.method == "POST":
        try:
            # --- Product fields ---
            name = request.POST.get("name")
            category_id = request.POST.get("category")
            subcategory_id = request.POST.get("subcategory")
            size_type_id = request.POST.get("size_type")
            purchase_price = request.POST.get("purchase_price")
            selling_price = request.POST.get("selling_price")
            discount = request.POST.get("discount") or 0
            description = request.POST.get("description")

            category = Category.objects.get(id=category_id) if category_id else None
            subcategory = SubCategory.objects.get(id=subcategory_id) if subcategory_id else None
            size_type = SizeType.objects.get(id=size_type_id) if size_type_id else None

            # Create Product
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

            # --- Variants ---
            sizes = request.POST.getlist("variant_size[]")
            colors = request.POST.getlist("variant_color[]")
            quantities = request.POST.getlist("variant_quantity[]")
            for i in range(len(sizes)):
                if sizes[i] and colors[i]:
                    qty = int(quantities[i] or 0)
                    ProductVariant.objects.create(
                        product=product,
                        size=sizes[i],
                        color=colors[i],
                        quantity=qty,
                        availability_count=qty  # set initial availability_count equal to quantity
                    )

            # --- Images ---
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

def variant_lookup(request):
    size = request.GET.get('size')
    color = request.GET.get('color')
    product_id = request.GET.get('product_id')
    try:
        variant = ProductVariant.objects.get(product_id=product_id, size=size, color=color)
        data = {
            'id': variant.id,
            'available': variant.is_available(),
            'current_quantity': variant.current_quantity,
            'price_after_discount': float(variant.price_after_discount),
            'selling_price': float(variant.selling_price),
            'bought_price': float(variant.bought_price),
        }
        return JsonResponse({'ok': True, 'variant': data})
    except ProductVariant.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'No variant'})
    

def products_view(request):
    return render(request, "shop/products_view.html", {"":""})



User = get_user_model()







def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.all()

    # Always pick a default variant
    current_variant = variants.first()

    if not current_variant:
        return render(request, "shop/product_detail.html", {
            "product": product,
            "variants": [],
            "current_variant": None,
            "is_favorite": False,
            "in_cart": False,
        })

    # Favorite check
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()

    # Cart check
    in_cart = False
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(
            user=request.user,
            variant=current_variant
        ).exists()

    return render(request, "shop/product_detail.html", {
        "product": product,
        "variants": variants,
        "current_variant": current_variant,
        "is_favorite": is_favorite,
        "in_cart": in_cart,
    })

def product_list(request):
    products = Product.objects.all()

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(request.user.favorites.values_list("product_id", flat=True))

    return render(request, "shop/product_list.html", {
        "products": products,
        "favorite_ids": favorite_ids,
    })


@login_required
def add_to_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    cart = request.session.get("cart", {})


    cart[str(variant_id)] = cart.get(str(variant_id), 0) + 1
    request.session["cart"] = cart


    return JsonResponse({"status": "success", "message": "Added to cart"})

@login_required
def toggle_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    cart_item = CartItem.objects.filter(user=request.user, variant=variant).first()

    if cart_item:
        cart_item.delete()  # REMOVE from cart
    else:
        CartItem.objects.create(user=request.user, variant=variant)  # ADD this exact size+color

    return redirect("shop:product_detail", product_id=variant.product.id)


@login_required
def add_to_favorite(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    fav = request.session.get("favorites", [])


    if product_id not in fav:
        fav.append(product_id)


    request.session["favorites"] = fav


    return JsonResponse({"status": "success", "message": "Added to favorites"})

def toggle_favorite(request, product_id):
    if not request.user.is_authenticated:
        return redirect("login")

    product = get_object_or_404(Product, id=product_id)

    fav, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        fav.delete()  # means already favorite → remove

    return redirect(request.META.get("HTTP_REFERER", "product_list"))


# Expense 

from django.shortcuts import render, redirect
from .models import Expense
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, DecimalField

@login_required
def add_expense(request):
    admin_users = User.objects.filter(is_staff=True)

    if request.method == "POST":
        amount = request.POST.get("amount")
        comment = request.POST.get("comment")
        type = request.POST.get("type")
        user_id = request.POST.get("user")

        Expense.objects.create(
            user_id=user_id,
            amount=amount,
            comment=comment,
            type=type
        )

        return redirect("shop:expense_list")

    return render(request, "shop/add_expense.html", {
        "admin_users": admin_users
    })


def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, "shop/expense_list.html", {"expenses": expenses})


@staff_member_required
def profit_report(request):

    # 1. Profit from sold products
    product_profit = ProductVariant.objects.annotate(
        sold_units=F("quantity") - F("availability_count")-F("in_delivery"),
        revenue=ExpressionWrapper(
            F("sold_units") * (F("product__selling_price") - F("product__purchase_price") - 20),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    ).aggregate(
        total_profit=Sum("revenue")
    )["total_profit"] or 0

    # 2. Expenses (money paid out)
    expense_out = Expense.objects.filter(
        type__in=["Extra offer", "Ads", "Other"]
    ).aggregate(
        total_out=Sum("amount")
    )["total_out"] or 0

    # 3. Extra gain (money received)
    expense_in = Expense.objects.filter(
        type="Extra gain"
    ).aggregate(
        total_in=Sum("amount")
    )["total_in"] or 0

    # 4. Final profit
    final_profit = product_profit - expense_out + expense_in

    return render(request, "shop/profit_report.html", {
        "profit": final_profit,
        "product_profit": product_profit,
        "expense_out": expense_out,
        "expense_in": expense_in,
    })

@staff_member_required
def balance(request):

    # ---- Table 1: Summary per user ----
    user_totals = (
        Expense.objects.values("user__username")
        .annotate(total=Sum("amount"))
        .order_by("user__username")
    )

    # ---- Table 2: List of expenses (exclude Justfit) ----
    expenses = Expense.objects.exclude(user__username="Justfit").order_by("-date")

    # ---- List of admin users (to change user in table rows) ----
    admin_users = User.objects.filter(is_staff=True)

    return render(request, "shop/balance.html", {
        "user_totals": user_totals,
        "expenses": expenses,
        "admin_users": admin_users
    })

@staff_member_required
def update_expense_user(request, pk):
    expense = Expense.objects.get(pk=pk)
    new_user_id = request.POST.get("user")

    if new_user_id:
        expense.user_id = new_user_id
        expense.save()

    return redirect("shop:balance")



@login_required
def add_credit(request):
    admin_users = User.objects.filter(is_staff=True)

    if request.method == "POST":
        amount = request.POST.get("amount")
        comment = request.POST.get("comment")
        user_id = request.POST.get("user")

        Credit.objects.create(
            user_id=user_id,
            amount=amount,
            comment=comment
        )

        return redirect("shop:credit_list")

    return render(request, "shop/add_credit.html", {
        "admin_users": admin_users
    })

def credit_list(request):
    credits = Credit.objects.all().order_by("-date")
    return render(request, "shop/credit_list.html", {"credits": credits})


@staff_member_required
def balance_credit(request):

    # ---- Summary for Credits ----
    credit_totals = (
        Credit.objects.values("user__username")
        .annotate(total=Sum("amount"))
        .order_by("user__username")
    )

    # ---- Full Credit List ----
    credits = Credit.objects.exclude(user__username="Justfit").order_by("-date")

    admin_users = User.objects.filter(is_staff=True)

    return render(request, "shop/balance_credit.html", {
        "credit_totals": credit_totals,
        "credits": credits,
        "admin_users": admin_users
    })

@staff_member_required
def update_credit_user(request, pk):
    credit = Credit.objects.get(pk=pk)
    new_user_id = request.POST.get("user")

    if new_user_id:
        credit.user_id = new_user_id
        credit.save()
    return redirect("shop:balance_credit")
