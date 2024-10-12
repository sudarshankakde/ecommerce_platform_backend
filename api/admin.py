from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, WholesalerProfile, RetailerProfile,Category, Product, ProductImage, ProductReview,Order
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 'is_wholesaler', 'is_retailer')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'is_admin', 'is_staff', 'is_wholesaler', 'is_retailer')
    
admin.site.register(User, UserAdmin)
admin.site.register(WholesalerProfile)
admin.site.register(RetailerProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductReview)
admin.site.register(Order)