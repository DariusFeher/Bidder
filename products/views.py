import datetime
from datetime import timedelta

import pytz
from auctions.forms import AuctionForm
from auctions.models import Auction
from auctions.utils import (get_bidders_product, get_no_bidders_product,
                            get_no_bids_product)
from bidnbuy.utils import filter_products
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from favourites.models import Favourite
from places.fields import PlacesField
from users.models import Account

from .forms import ProductForm, SearchForm
from .models import Product
from .tasks import send_bidding_confirmation, send_outbidding_email
from .utils import handle_file, handle_uploaded_file

# Create your views here.
conditions = {
            '1': _('New'),
            '2': _('Used')
        }
currencies = {
            ('1', _('LEI')),
            ('2', _('USD (US$)')),
            ('3', _('EUR (€)')),
            ('4', _('GBP (£)'))
        }

@login_required(login_url='/login/')
def newProduct(request):
    form = ProductForm()
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            title = request.POST.get('title')
            description = request.POST.get('description')
            condition = request.POST.get('condition')
            currency = request.POST.get('currency')
            starting_price = request.POST.get('starting_price')
            phone_number = request.POST.get('phone_number')
            picture1 = request.FILES.get('picture1')
            picture2 = request.FILES.get('picture2')
            picture3 = request.FILES.get('picture3')
            picture4 = request.FILES.get('picture4')
            picture5 = request.FILES.get('picture5')
            picture6 = request.FILES.get('picture6')
            location_0 = request.POST.get('location_0')
            location_1 = request.POST.get('location_1')
            location_2 = request.POST.get('location_2')
            location = str(location_0 + ", " + location_1 + ", " + location_2)
            date = datetime.datetime.combine(form.cleaned_data['end_date'], form.cleaned_data['end_hour'])
            product = Product(
                              title=title,
                              description=description,
                              condition=condition,
                              starting_price=starting_price,
                              end_date=date,
                              picture1=picture1,
                              picture2=picture2,
                              picture3=picture3,
                              picture4=picture4,
                              picture5=picture5,
                              picture6=picture6,
                              phone_number=phone_number,
                              currency=currency,
                              location=location,
                              seller=request.user
                              )
            product.save()
            messages.success(request, "Product added successfully!")
            detail_page = product.get_detail_url()
            return redirect(detail_page)
        else:
            form.add_error(NON_FIELD_ERRORS, _("Something went wrong..."))
    context = {'form': form}
    return render(request, 'products/new_product.html', context)

@login_required(login_url='/login/')
def editProduct(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=get_object_or_404(Product, pk=pk))
        if form.is_valid():
            date = datetime.datetime.combine(form.cleaned_data['end_date'], form.cleaned_data['end_hour'])
            pictures_changes = False
            picture1 = handle_file(form.cleaned_data['picture1'], product.picture1, False)
            picture2 = handle_file(form.cleaned_data['picture2'], product.picture2, form.cleaned_data['delete2'])
            picture3 = handle_file(form.cleaned_data['picture3'], product.picture3, form.cleaned_data['delete3'])
            picture4 = handle_file(form.cleaned_data['picture4'], product.picture4, form.cleaned_data['delete4'])
            picture5 = handle_file(form.cleaned_data['picture5'], product.picture5, form.cleaned_data['delete5'])
            picture6 = handle_file(form.cleaned_data['picture6'], product.picture6, form.cleaned_data['delete6'])

            if (picture2 is None or picture3 is None or picture4 is None or
                picture5 is None or picture6 is None):
                pictures_changes = True
            location_0 = request.POST.get('location_0')
            location_1 = request.POST.get('location_1')
            location_2 = request.POST.get('location_2')
            location = str(location_0 + ", " + location_1 + ", " + location_2)

            if (form.cleaned_data['title'] != product.title or
                form.cleaned_data['description'] != product.description or
                form.cleaned_data['condition'] != product.condition or
                form.cleaned_data['starting_price'] != product.starting_price or
                date != product.end_date or
                picture1 != product.picture1 or 
                picture2 != product.picture2 or 
                picture3 != product.picture3 or 
                picture4 != product.picture4 or 
                picture5 != product.picture5 or 
                picture6 != product.picture6 or
                pictures_changes):
                
                Product.objects.filter(pk=pk).update(
                        title=form.cleaned_data['title'],
                        description=form.cleaned_data['description'],
                        condition=form.cleaned_data['condition'],
                        starting_price=form.cleaned_data['starting_price'],
                        currency=form.cleaned_data['currency'],
                        phone_number=form.cleaned_data['phone_number'],
                        location=location,
                        end_date=date,
                        picture1=picture1,
                        picture2=picture2,
                        picture3=picture3,
                        picture4=picture4,
                        picture5=picture5,
                        picture6=picture6,
                        seller=request.user,
                        last_updated=datetime.datetime.now(pytz.timezone('Europe/Bucharest'))
                    )
            detail_page = product.get_detail_url()
            return redirect(detail_page)
        else:
            form.add_error(NON_FIELD_ERRORS, _("Something went wrong..."))
            context = {"form": form, 'object': product}
            return render(request, 'products/edit_product.html', context)
    else:
        template = 'products/edit_product.html'
        form = ProductForm(instance=product)
        context = {"form": form, 'object': product}
        return render(request, template, context)

@login_required(login_url='/login/')
def deleteProduct(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    product.delete()
    messages.success(request, _("Product ") + product.title + _(" deleted successfully"))
    return redirect('/')


@login_required(login_url='/login/')
def detailPage(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {'object': product}
    auctionForm = AuctionForm(product=product, bidder=request.user)
    context['auctionForm'] = auctionForm
    if request.method == "POST":
        auctionForm = AuctionForm(request.POST, product=product, bidder=request.user)
        if auctionForm.is_valid() and timezone.now() + timedelta(hours=3) <= product.end_date:
            auction = Auction(
                bidder=request.user,
                product=product,
                bid_amount=auctionForm.cleaned_data.get('bid_amount')
            )
            auction.save()
            Product.objects.filter(pk=pk).update(
                last_bid=auctionForm.cleaned_data.get('bid_amount')
            )
            product = get_object_or_404(Product, pk=pk)
            context = {'object': product}
            user = Account.objects.get(email=request.user)
            send_bidding_confirmation.delay(request.LANGUAGE_CODE, user.pk, product.pk)
            messages.success(request,  _('Your bid has been recorded.'))
            last_auction = Auction.objects.filter(product=product).order_by('-bid_time')
            if len(last_auction) >= 2 and last_auction[1].bidder.email != request.user.email:
                send_outbidding_email.delay(request.LANGUAGE_CODE, product.pk, last_auction[1].pk)
        else:
            if timezone.now() + timedelta(hours=3) > product.end_date:
                messages.error(request,  _('Auction has finished!'))
            else:
                messages.error(request,  _('Something went wrong...'))
        context['auctionForm'] = auctionForm
    last_auction = Auction.objects.filter(product=product).order_by('-bid_time')
    if len(last_auction):
        context['last_auction'] = last_auction[0]
    else:
        context['last_auction'] = ""
    form = ProductForm(instance=product)
    context['form'] = form
    context['bidders'] = get_no_bidders_product(product)
    context['bids'] = get_no_bids_product(product)
    if len(Favourite.objects.filter(user=request.user, product=product)):
        context['favourite'] = True
    else:
        context['favourite'] = False
    template_name = 'products/detail_product.html'
    return render(request, template_name, context)

@login_required(login_url='login')
def myProductsPage(request):
    products = Product.objects.filter(seller=request.user).order_by("end_date")
    products_copy = products
    if request.method == 'GET':
        searchForm = SearchForm()
    else:
        searchForm = SearchForm(request.POST)
        if searchForm.is_valid():
            cd = searchForm.cleaned_data
            products = filter_products(cd, products)
    msg = _('You currently have no ads...')
    if len(products_copy) != 0 and len(products) == 0:
        msg = _('There are no products matching your search...')
    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    favourites_list = []
    for product in page_obj:
        if len(Favourite.objects.filter(user=request.user, product=product)):
            favourites_list.append(product)
    products = Product.objects.all()
    return render(request, 'home.html', {'page_obj': page_obj,
                                        'range': range(1, page_obj.paginator.num_pages + 1),
                                        'favourites_list' : favourites_list,
                                        'title': _('Your products'),
                                        'no_items_msg': msg,
                                        'page_title': 'My products',
                                        'searchForm': searchForm,
                                        })

@login_required(login_url='login')
def myWishlistPage(request):
    products_ids = Favourite.objects.filter(user=request.user).values('product')
    products = Product.objects.filter(pk__in=products_ids).order_by("end_date")
    products_copy = products
    if request.method == 'GET':
        searchForm = SearchForm()
    else:
        searchForm = SearchForm(request.POST)
        if searchForm.is_valid():
            cd = searchForm.cleaned_data
            products = filter_products(cd, products)
    msg = _('You currently have no favourite ads...')
    if len(products_copy) != 0 and len(products) == 0:
        msg = _('There are no products matching your search...')
    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    favourites_list = []
    for product in page_obj:
        favourites_list.append(product)
    return render(request, 'home.html', {'page_obj': page_obj,
                                        'range': range(1, page_obj.paginator.num_pages + 1),
                                        'favourites_list' : favourites_list,
                                        'title': _('Wishlist products'),
                                        'no_items_msg': msg,
                                        'page_title': 'Wishlist',
                                        'searchForm': searchForm,
                                        })
