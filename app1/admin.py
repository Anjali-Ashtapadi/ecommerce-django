from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category,Account,Product, Cart, CartItem, Variation
# Register your models here.

class AccountAdmin(UserAdmin):
    list_display=('email','first_name','last_name','last_login','date_joined','is_active')
    list_display_links=('email','first_name','last_name')
    readonly_fields=('last_login','date_joined')
    ordering=('-date_joined',)

    filter_horizontal=()
    list_filter=()
    fieldsets=()

class CategoryAdmin(admin.ModelAdmin):
    # prepopulated_fields={'slug':('category_name',)}
    list_display=('category_name','slug',)


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('product_name',)}
    list_display=('product_name','price','stock','category','modified_date','is_available')

class VariationAdmin(admin.ModelAdmin):
    list_display=('product','variation_category','variation_values','is_active')
    list_editable =('is_active',)
    list_filter = ('product','variation_category','variation_values')

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id','date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_display =('product','cart','quantity','is_active')

admin.site.register(Category)
admin.site.register(Account,AccountAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem,CartItemAdmin)
admin.site.register(Variation,VariationAdmin)