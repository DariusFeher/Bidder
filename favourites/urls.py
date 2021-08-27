from django.contrib import admin
from django.urls import path
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('add_to_favourites/<pk>', views.newFavourite, name='newFavourite'),
    path('remove_from_favourites/<pk>', views.deleteFavourite, name='deleteFavourite'),
]