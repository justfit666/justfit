from django.contrib import admin

from . import models

admin.site.register(models.Product)
admin.site.register(models.ProductImage)
admin.site.register(models.ProductVariant)
admin.site.register(models.Expense)
admin.site.register(models.Category)
admin.site.register(models.SubCategory)
admin.site.register(models.Order)
admin.site.register(models.OrderItem)
