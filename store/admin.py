from re import L
from django.contrib import admin
from store.models import Category, Product, Vendor, Order, UserProfile, Announcement, OrderItem

# Register your models here.

admin.site.register(UserProfile)


@admin.register(Category)
class Category(admin.ModelAdmin):
    list_display = ['name', 'category_code', 'category_id', 'slug']

@admin.register(Product)
class Product(admin.ModelAdmin):
    list_display = ['name', 'product_code', 'category', 'vendor', 'price', 'deal_price', 'is_featured']
    list_editable = ['price', 'deal_price', 'is_featured',]

@admin.register(Vendor)
class Vendor(admin.ModelAdmin):
    list_display = ['name', 'vendor_id']

@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'is_active']

@admin.register(OrderItem)
class OrderItem(admin.ModelAdmin):
    list_display = ['order_name', 'product_name', 'price', 'amount']

    def order_name(self, instance):
        return instance.order
    def product_name(self, instance):
        return instance.product

@admin.register(Announcement)
class Announcement(admin.ModelAdmin):
    list_display = ['description', 'image']
