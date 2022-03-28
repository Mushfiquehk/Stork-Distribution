from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='home'),
    path('shop/', views.shop, name='all_products'), 
    path('shop/<slug:slug>/', views.category_list, name='category_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_summary, name='cart_summary'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('order_summary/<int:pk>/', views.order_summary, name='order_summary'),
    path('register/', views.register, name="register"),
]