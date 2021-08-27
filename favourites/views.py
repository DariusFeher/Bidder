from django.http import HttpResponse
from favourites.models import Favourite
from products.models import Product
from django.shortcuts import get_object_or_404, redirect

# Create your views here.

def newFavourite(request, pk):
    user = request.user
    product = Product.objects.get(pk=pk)
    if len(Favourite.objects.filter(user=user, product=product)) == 0:
        favourite = Favourite(
            user=user,
            product=product
        )
        favourite.save()
    return redirect(request.META['HTTP_REFERER'])

def deleteFavourite(request, pk):
    user = request.user
    product = Product.objects.get(pk=pk)
    if len(Favourite.objects.filter(user=user, product=product)):
        favourites = get_object_or_404(Favourite, user=user, product=product)
        favourites.delete()
        return HttpResponse("Removed from favourites")
    return HttpResponse("There is no such product in favourites")