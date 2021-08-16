from cProfile import label
import datetime
from multiprocessing import Condition

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField
from places.fields import PlacesField


from .models import Product

currencies = [
            ('1', _('LEI')),
            ('2', _('USD (US$)')),
            ('3', _('EUR (€)')),
            ('4', _('GBP (£)'))
        ]

conditions = [      
            ('1', _('New')),
            ('2', _('Used'))
        ]

class ProductForm(ModelForm):
    title = forms.CharField(label=_('Title'), max_length=100, help_text=_('Please set a suggestive title for your product which contains at least 5 characters'))
    description = forms.CharField(widget=forms.Textarea, max_length=3000, help_text=_('Please describe the product you are selling'), label=_('Description'))
    condition =  forms.ChoiceField(choices=conditions, label=_('Condition'))
    starting_price = forms.FloatField(localize=True, label=_('Starting price'), help_text=_('Please set the product\'s starting price'))
    end_date = forms.DateField()
    end_hour = forms.TimeField(input_formats = ['%I:%M %p'], widget=forms.TimeInput(), help_text=_('Please choose an ending date and time for the bidding'), label=_("End hour"))
    picture1 = forms.ImageField(label=_('Main image'), help_text=_('Please set a main image for your product'))
    picture2 = forms.ImageField(label=_('Image 2'), required=False)
    picture3 = forms.ImageField(label=_('Image 3'), required=False)
    picture4 = forms.ImageField(label=_('Image 4'), required=False)
    picture5 = forms.ImageField(label=_('Image 5'), required=False)
    picture6 = forms.ImageField(label=_('Image 6'), required=False)
    delete1 = forms.BooleanField(required=False)
    delete2 = forms.BooleanField(required=False)
    delete3 = forms.BooleanField(required=False)
    delete4 = forms.BooleanField(required=False)
    delete5 = forms.BooleanField(required=False)
    delete6 = forms.BooleanField(required=False)
    currency = forms.ChoiceField(choices=currencies, label=_('Currency'))
    phone_number = PhoneNumberField(widget=forms.TextInput(), label=_("Phone number"), help_text=_('Please enter a phone number (e.g. +40792011221).'))
    phone_number.error_messages['invalid'] = _('Enter a valid phone number (e.g. +40792011221).')
    location = PlacesField()

    class Meta:
        model = Product
        fields = ["title", "description", "condition", "end_date", "end_hour", "picture1",
                  "picture2", "picture3", "picture4", "picture5", "picture6", "delete6", 
                  "delete2", "delete3", "delete4", "delete5", "phone_number", "currency",
                  "location"]

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError(_("The title should contain at least 5 characters."))
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 5:
            raise ValidationError(_("The description should contain at least 5 characters."))
        return description
    
    def clean_starting_price(self):
        starting_price = self.cleaned_data.get('starting_price')
        if starting_price < 0:
            raise ValidationError(_("The starting price should be greater than or equal to 0."))
        return starting_price
    
    def clean_end_hour(self):
        end_date = self.cleaned_data.get('end_date')
        end_hour = self.cleaned_data.get('end_hour')
        print("HERE ")
        print(end_hour)
        current_datetime = datetime.datetime.combine(end_date, end_hour)
        if current_datetime < datetime.datetime.now():
            raise ValidationError(_("The date and time cannot be in the past."))
        return end_hour
    
    
    