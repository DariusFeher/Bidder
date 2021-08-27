import datetime
import favourites
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from products.models import Product

from favourites.models import Favourite
from products.forms import SearchForm
from django.contrib.postgres.search import SearchVector
from django.utils.translation import gettext as _
from django.db.models import Q
from users.models import Account
from itertools import chain
from .utils import filter_products
# Create your views here.

sellers = [      
            ('1', _('New')),
            ('2', _('Used'))
        ]

@login_required(login_url='login')
def homePage(request):
    if request.method == 'GET':
        searchForm = SearchForm()
        products = Product.objects.all()
    else:
        searchForm = SearchForm(request.POST)
        if searchForm.is_valid():
            cd = searchForm.cleaned_data
            products = Product.objects.all()
            products = filter_products(cd, products)
        else:
            products = Product.objects.all()
    if len(products):
        products = products.filter(end_date__gte=datetime.datetime.now().date()).order_by("end_date")
    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user = request.user
    favourites_list = []
    for product in page_obj:
        if len(Favourite.objects.filter(user=user, product=product)):
            favourites_list.append(product)
    if len(Product.objects.all()) == 0:
        msg = _('There are no ads available at the moment...')
        if len(products) == 0:
            msg = _('There are no products matching your search...')
    else:
        msg = _('There are no products matching your search...')
        
    return render(request, 'home.html', {'page_obj': page_obj,
                            'range': range(1, page_obj.paginator.num_pages + 1),
                            'favourites_list' : favourites_list,
                            'title': _('Available products'),
                            'no_items_msg': msg,
                            'page_title': _('Home'),
                            'searchForm': searchForm,
                            })
