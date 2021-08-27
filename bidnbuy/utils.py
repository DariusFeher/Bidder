
from datetime import timedelta
from products.models import Product

from products.forms import SearchForm

from django.db.models import Q
from users.models import Account
def filter_products(cd, products):
    # FILTER SEARCH TERM
    search_term = cd['search_term']
    if search_term:
        products = products.filter(Q(title__icontains=search_term) | Q(description__icontains=search_term))
    
    # FILTER SELLER
    seller = cd['seller']
    if seller:
        if Account.objects.filter(pk=seller):
            seller = Account.objects.get(pk=seller)
            print(seller)
            if products and seller:
                products = products.filter(Q(seller=seller))
    
    # FILTER CONDITION
    condition = cd['condition']
    if condition != '0' and condition:
        if products:
            products = products.filter(Q(condition=condition))

    # FILTER STARTING PRICE
    starting_price = cd['starting_price']
    if starting_price:
        if products:
            products = products.filter(Q(starting_price__lt=starting_price))
        
    # FILTER END DATE
    end_date = cd['end_date']
    if end_date:
        if products:
            products = products.filter(Q(end_date__lte=end_date + timedelta(days=1)))

    # FILTER LOCATION
    locations = cd['location']
    if len(locations):
        results = []
        if products:
            products_copy = products
            products = products_copy.filter(Q(location__icontains=SearchForm.locations[int(locations[0]) - 1][1]))
            for i in range(1, len(locations)):
                place = SearchForm.locations[int(locations[i]) - 1][1]
                products = products | products_copy.filter(Q(location__icontains=place))
    
    return products