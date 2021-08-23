from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from products.models import Product
from urllib3 import HTTPResponse
from datetime import datetime

from .tasks import send_email_task
# Create your views here.

@login_required(login_url='login')
def homePage(request):
    products = Product.objects.all()
    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    products = Product.objects.all()
    print(datetime.now())
    # for product in products:
    #     if product.end_date = 
    return render(request, 'home.html', {'page_obj': page_obj, 'range': range(1, page_obj.paginator.num_pages + 1)})
