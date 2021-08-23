from cProfile import label
import datetime
from multiprocessing import Condition

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField
from places.fields import PlacesField


from .models import Auction

class AuctionForm(ModelForm):
    bid_amount = forms.FloatField(localize=True, label=_('Amount'))
    # Choose a value greater than the last bid and starting price

    def __init__(self, *args, **kwargs):
        self.bidder = kwargs.pop('bidder')
        self.product = kwargs.pop('product')
        super(AuctionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Auction
        fields = ["bidder", "product", "bid_time", "bid_amount"]
        exclude = ["bidder", "product", "bid_time"] # not editable fields
    
    def clean(self):
        bid_amount = self.data.get('bid_amount')
        try:
            bid_amount = float(bid_amount)
        except:
            raise forms.ValidationError("")
        if bid_amount < 0:
            raise forms.ValidationError(_("The amount should be greater than or equal to 0."))
        if bid_amount <= self.product.last_bid:
            raise forms.ValidationError(_("The amount should be greater than the last bid."))
        if bid_amount < self.product.starting_price:
            raise forms.ValidationError(_("The amount should be greater than or equal to the starting price."))
        return self.cleaned_data


