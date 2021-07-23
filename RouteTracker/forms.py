from django.forms import ModelForm
from django import forms
from .models import Route


class RouteForm(ModelForm):    
    class Meta:
        model = Route
        verbose_name = "Route List"
        exclude = ('routeId', 'user', 'dateAdded','calcSOC','fileName')
        widgets = {
            
        }



