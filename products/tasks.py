from timeit import repeat
from users.models import Account
from .models import Product
from auctions.models import Auction
from auctions.utils import get_no_bidders_product, get_no_bids_product
from background_task import background
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils.translation import gettext as _
from django.utils import translation
from django.utils.translation import get_language


@background
def send_bidding_confirmation(language, pk_user, pk_product):
    translation.activate(language)
    user = Account.objects.get(pk=pk_user)
    product = Product.objects.get(pk=pk_product)
    current_site = Site.objects.get_current().domain
    template = get_template('auctions/bidding_confirmation.html')
    context = {
        'user': user.username,
        'product': product,
        'domain': str(current_site).rstrip("/"),
        'bidders': get_no_bidders_product(product),
        'bids': get_no_bids_product(product),
    }
    content = template.render(context)
    email_subject = (user.username + _(', your bidding is the highest one at the moment!'))
    email = EmailMessage(subject=email_subject,
                body=content,
                from_email=settings.EMAIL_FROM_USER,
                to=[user.email])
    email.content_subtype = "html"
    email.send()
    return "Bidding confirmation email sent"

@background
def send_outbidding_email(language, pk_product, pk_last_auction):
    product = Product.objects.get(pk=pk_product)
    translation.activate(language)
    last_auction = Auction.objects.get(pk=pk_last_auction)
    current_site = Site.objects.get_current().domain
    template = get_template('auctions/outbidding_information.html')
    email_to = last_auction.bidder.email
    username = last_auction.bidder.username
    context = {
        'user': username,
        'product': product,
        'domain': str(current_site).rstrip("/"),
        'bidders': get_no_bidders_product(product),
        'bids': get_no_bids_product(product),
    }
    content = template.render(context)
    email_subject = (_('Outbid! You need to raise your bid for ') + product.title)
    email = EmailMessage(subject=email_subject,
                body=content,
                from_email=settings.EMAIL_FROM_USER,
                to=[email_to])
    email.content_subtype = "html"
    email.send()
    return "Outbidding email sent"
