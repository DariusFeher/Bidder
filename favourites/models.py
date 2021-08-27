from django.db import models
from products.models import Product
from users.models import Account

class Favourite(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    favourite_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.user.username) + ", " + str(self.product.title)