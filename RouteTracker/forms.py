from django.forms import ModelForm
from django.contrib.postgres.forms import SplitArrayField
from django import forms
from .models import Route


class RouteForm(ModelForm):
    departure = SplitArrayField(forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})), 20, remove_trailing_nulls=True)
    transit = SplitArrayField(forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})), 20, remove_trailing_nulls=True)
    arrival = SplitArrayField(forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})), 20, remove_trailing_nulls=True)
    stay = SplitArrayField(forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})), 20, remove_trailing_nulls=True)

    class Meta:
        model = Route
        verbose_name = "Route List"
        exclude = ('routeId', 'user', 'dateAdded','calcSOC','fileName')
        widgets = {
            
        }



