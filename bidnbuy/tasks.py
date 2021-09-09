from datetime import timedelta
from timeit import repeat
from django.core.mail import EmailMessage

from auctions.models import Auction
from auctions.utils import get_no_bidders_product, get_no_bids_product
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext as _
from products.models import Product

from background_task import background

@background()
def send_email_task():
    products = Product.objects.all()
    current_site = Site.objects.get_current().domain
    for product in products:
        if product.end_date <= timezone.now() + timedelta(hours=3) and product.finished_email_sent is False:
            last_auction = Auction.objects.filter(product=product).order_by('-bid_time')
            context_owner = {
                'winner' : '',
                'product': product,
                'domain': str(current_site).rstrip("/"),
                'bidders': get_no_bidders_product(product),
                'bids': get_no_bids_product(product),
            }
            if len(last_auction):
                last_bidder_email = last_auction[0].bidder.email
                context_winner = {
                    'user': last_auction[0].bidder.username,
                    'product': product,
                    'domain': str(current_site).rstrip("/"),
                    'bidders': get_no_bidders_product(product) - 1,
                    'bids': get_no_bids_product(product),
                }
                template_winner = get_template('auctions/bidding_finished_winner_confirmation.html')
                content_winner = template_winner.render(context_winner)
                subject_winner = ("Congratulations ") + last_auction[0].bidder.username + _(", you won the auction!")
                email_winner = EmailMessage(
                    subject=subject_winner,
                    body=content_winner,
                    from_email=settings.EMAIL_FROM_USER,
                    to=[last_bidder_email]
                )
                email_winner.content_subtype = "html"
                email_winner.send()
                context_owner['winner'] = last_auction[0].bidder
                
            template_owner = get_template('auctions/bidding_finished_owner_confirmation.html')
            content_owner = template_owner.render(context_owner)
            subject_owner = product.seller.username + _(", your auction has finished!")
            email_owner = EmailMessage(
                subject=subject_owner,
                body=content_owner,
                from_email=settings.EMAIL_FROM_USER,
                to=[product.seller.email]
            )
            email_owner.content_subtype = "html"
            email_owner.send()
            product.finished_email_sent = True
            product.save()
    return "Send email task done"
