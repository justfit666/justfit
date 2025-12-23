# from django.contrib import admin

# from . import models

# admin.site.register(models.Product)
# admin.site.register(models.ProductImage)
# admin.site.register(models.ProductVariant)
# admin.site.register(models.Expense)
# admin.site.register(models.Category)
# admin.site.register(models.SubCategory)
# admin.site.register(models.Order)
# admin.site.register(models.OrderItem)
# admin.site.register(models.Credit)

from django.contrib import admin
from .models import (
    SizeType, Category, SubCategory, Product, 
    ProductVariant, ProductImage, Favorite, 
    CartItem, Order, OrderItem, Expense, Credit
)

# --- Inlines (Allow editing related items inside the parent model) ---

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)

# --- Admin Registrations ---

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subcategory', 'selling_price', 'total_quantity_available')
    list_filter = ('category', 'subcategory')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline, ProductVariantInline]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'cutomer_name', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('cutomer_name', 'id')
    inlines = [OrderItemInline]

# @admin.register(SubCategory)
# class SubCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'category')
#     list_filter = ('category',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'date')
    list_filter = ('type', 'date', 'user')

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'date')
    list_filter = ('date', 'user')

# Registering the remaining models with default options
# admin.site.register(SizeType)
# admin.site.register(Category)
# admin.site.register(Favorite)
# admin.site.register(CartItem)
# admin.site.register(ProductVariant) # Optional: Already accessible via Product inline
# admin.site.register(ProductImage)   # Optional: Already accessible via Product inline
# admin.site.register(OrderItem)      # Optional: Already accessible via Order inline
