from django.contrib import admin
from store.models import Category, Product, Order, UserProfile, Announcement, OrderItem


@admin.register(UserProfile)
class UserProfile(admin.ModelAdmin):
    list_display = ['certificates']


@admin.register(Category)
class Category(admin.ModelAdmin):
    list_display = ['name', 'slug']
    ordering = ('id',)


@admin.register(Product)
class Product(admin.ModelAdmin):
    list_display = ['name', 'price', 'amount', 'image', 'is_active']
    list_filter = ('category',)
    list_editable = ('image', 'is_active')
    search_fields = ('name',)
    ordering = ('-id',)


@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'is_active']
    ordering = ('-id',)


@admin.register(OrderItem)
class OrderItem(admin.ModelAdmin):
    list_display = ['order_name', 'product_name', 'price', 'amount']
    list_filter = ('order__name',)

    def order_name(self, instance):
        return instance.order

    def product_name(self, instance):
        return instance.product


@admin.register(Announcement)
class Announcement(admin.ModelAdmin):
    list_display = ['description', 'image']


admin.site.site_header = 'Stork Backstore'
