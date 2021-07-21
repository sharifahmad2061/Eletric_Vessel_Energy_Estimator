from django.forms import ModelForm
from allauth.account.forms import SignupForm
from django import forms
from .models import Route, CustomUser


class RouteForm(ModelForm):    
    class Meta:
        model = Route
        verbose_name = "Route List"
        exclude = ('routeId', 'user', 'dateAdded','calcSOC','fileName')



