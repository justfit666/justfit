# shop/urls.py
from django.urls import path
from . import views

from . import views

from django.contrib.auth import views as auth_views

# from .auth_views import *
# from .product_views import *
# from .variant_views import *
# from .favorite_cart_views import *
# from .expense_views import *
# from .credit_views import *
# from .order_views import *


app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('view', views.products_view, name='products_view'),
    path('login/', views.custom_login, name='login'),
    path('signup/', views.custom_signup, name='signup'),

    path('logout/', auth_views.LogoutView.as_view(next_page='shop:login'), name='logout'),
    #path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('ajax/variant/', views.variant_lookup, name='variant_lookup'),
        # New pages
    #path('profit/', views.profit_report, name='profit_report'),
    path('products/fast-add/', views.fast_add_product, name='fast_add_product'),

    path('products/table/', views.product_table, name='product_table'),
    path('products/update-variant/<int:variant_id>/', views.update_variant_field, name='update_variant_field'),
    path("products/", views.product_list, name="product_list"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),


    # ⭐ Add this
    path("favorite/<int:product_id>/toggle/", views.toggle_favorite, name="toggle_favorite"),
    path("cart/add/<int:variant_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/toggle/<int:variant_id>/", views.toggle_cart, name="toggle_cart"),

    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.add_expense, name="add_expense"),
    path("profit/", views.profit_report, name="profit_report"),
    path("expense/update-user/<int:pk>/", views.update_expense_user, name="update_expense_user"),
    path("expense/balance/", views.balance, name="balance"),
    path("balance_credit/", views.balance_credit, name="balance_credit"),
    path("credit/add/", views.add_credit, name="add_credit"),
    path("credits/", views.credit_list, name="credit_list"),
    path("credit/update/<int:pk>/", views.update_credit_user, name="update_credit_user"),
    path("api/product/<int:product_id>/filter/", views.get_filtered_variant, name="variant_filter"),
    path("orders/", views.admin_order_list, name="admin_order_list"),
    # path("orders/bulk-update/", views.bulk_update_orders, name="bulk_update_orders"),
    path("orders/update-field/<int:order_id>/", views.ajax_update_order_field, name="ajax_update_order_field"),
    path("orders/bulk-update/", views.bulk_update_orders, name="bulk_update_orders"),
    path("orders/update-status/<int:order_id>/", views.update_order_status, name="update_order_status"),
    path("orders/update-item-status/<int:item_id>/", views.update_item_status, name="update_item_status"),











]
