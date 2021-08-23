from django.db import models
from django.utils import timezone
from products.models import Product
from users.models import Account

class Auction(models.Model):
    bidder = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bid_time = models.DateTimeField(auto_now_add=True)
    bid_amount = models.FloatField()
    
    def __str__(self) -> str:
        return str(self.bidder.email) + ", " + str(self.product.title)

    def get_date_time_in_local_timezone(self):
        return timezone.localtime(self.bid_time)
