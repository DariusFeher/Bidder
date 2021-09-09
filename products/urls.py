from django.contrib import admin
from django.urls import path
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('products/new/', views.newProduct, name="new-product"),
    path('products/mywishlist/', views.myWishlistPage, name='mywishlist'),
    path('products/myproducts/', views.myProductsPage, name='myproducts'),
    path('products/<pk>/', views.detailPage, name='detail-product'),
	path('products/<pk>/edit', views.editProduct, name='edit-product'),
    path('products/<pk>/delete', views.deleteProduct, name='delete')
]