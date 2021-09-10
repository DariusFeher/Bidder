from .models import Auction

def get_no_bids_product(product):
    return Auction.objects.filter(product=product).count()

def get_no_bidders_product(product):
    return Auction.objects.filter(product=product).distinct('bidder').count()

def get_bidders_product(product, bidder):
    return Auction.objects.filter(product=product).values('bidder').distinct('bidder')
