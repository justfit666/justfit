from django.contrib import admin
from .models import (
    Product, ProductImage, ProductVariant,
    Expense,Category,SubCategory
)

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductVariant)
admin.site.register(Expense)
admin.site.register(Category)
admin.site.register(SubCategory)
