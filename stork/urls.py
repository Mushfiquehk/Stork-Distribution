from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('store.urls')),
    path('logout/', views.user_logout, name='logout'),
    # path("__reload__/", include("django_browser_reload.urls")),
    path('', include('django.contrib.auth.urls')),
] 