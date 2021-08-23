import calendar
from datetime import datetime, timedelta, timezone

from django.db import models
from django.shortcuts import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from places.fields import PlacesField
from requests import request
from users.models import Account

from .utils import date_diff_in_seconds, dhms_from_seconds

conditions = [
            ('1', _('New')),
            ('2', _('Used'))
          ]

currencies = [
            ('1', _('LEI')),
            ('2', _('USD (US$)')),
            ('3', _('EUR (€)')),
            ('4', _('GBP (£)'))
]

class Product(models.Model):
    seller = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    date_posted = models.DateTimeField(verbose_name='Date posted', auto_now_add=True)
    last_updated = models.DateTimeField(verbose_name='Date updated', auto_now=True)
    description = models.CharField(max_length=3000)
    condition = models.CharField(max_length=20, choices=conditions)
    starting_price = models.FloatField(default=0.0)
    last_bid = models.FloatField(default=0.0)
    end_date = models.DateTimeField()
    picture1 = models.ImageField(default="placeholder.png")
    picture2 = models.ImageField(default="placeholder.png", null=True, blank=True)
    picture3 = models.ImageField(default="placeholder.png", null=True, blank=True)
    picture4 = models.ImageField(default="placeholder.png", null=True, blank=True)
    picture5 = models.ImageField(default="placeholder.png", null=True, blank=True)
    picture6 = models.ImageField(default="placeholder.png", null=True, blank=True)
    phone_number = PhoneNumberField()
    currency = models.CharField(max_length=20, choices=currencies)
    location = PlacesField(null=True)
    finished_email_sent = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title
    
    def get_date_from_datetime(self) -> str:
      return self.end_date.strftime("%Y-%m-%d")
    
    def get_hour_from_datetime(self) -> str:
      return self.end_date.strftime("%I:%M %p")
    
    def get_date(self) -> str:
      return self.end_date.strftime("%d %B %Y at %I:%M %p")
    
    def get_end_date_translated(self) -> str:
      month_no = int(self.end_date.strftime("%m"))
      return self.end_date.strftime("%d " + _(calendar.month_name[month_no]) + " %Y " + _("at") + " %I:%M %p")
    
    def get_date_posted_translated(self) -> str:
      month_no = int(self.date_posted.strftime("%m"))
      return self.date_posted.strftime("%d " + _(calendar.month_name[month_no]) + " %Y, " + " %I:%M %p")
    
    def get_date_posted_string(self) -> str:
      return self.date_posted.strftime("%d %B %Y, %I:%M %p")
    
    def get_seller(self):
      return self.seller

    def get_detail_url(self):
      return reverse('detail-product', kwargs={'pk' : self.pk})
    
    def get_delete_url(self):
    	return reverse('delete-product', kwargs={'pk' : self.pk})
    
    def get_end_date_ISO_formatted(self):
      return self.end_date.strftime("%d %B %Y %H:%M")
    
    def get_time_remaining(self):
      return ("%d days, %d hrs, %d mins" % dhms_from_seconds(date_diff_in_seconds(self.end_date, datetime.now(timezone.utc) + timedelta(hours = 3))))





