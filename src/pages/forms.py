from django import forms
from .models import Artist

class RawForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['artistID']