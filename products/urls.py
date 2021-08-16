from django.contrib import admin
from django.urls import path
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('products/new/', views.newProduct, name="new-product"),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('products/<pk>/', views.detailPage, name='detail-product'),
	path('products/<pk>/edit/', views.editProduct, name='edit-product'),
    path('products/<pk>/delete/', views.deleteProduct, name='delete')
]