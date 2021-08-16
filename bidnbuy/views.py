from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from urllib3 import HTTPResponse
from products.models import Product

# Create your views here.

@login_required(login_url='login')
def homePage(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, "home.html", context)