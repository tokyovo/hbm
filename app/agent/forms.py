# forms.py
from django import forms
from .models import Collection

class CollectionSelectForm(forms.Form):
    collection = forms.ModelChoiceField(
        queryset=Collection.objects.all(),
        label="Select Collection",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
