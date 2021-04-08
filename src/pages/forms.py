from django import forms
from .models import Artist

class RawForm(forms.ModelForm):
    artistID       = forms.CharField(label='', widget=forms.TextInput(
                            attrs={
                                "placeholder": "Search",
                                "size": 50,
                                'class': 'form-control',
                                'style': 'margin-bottom: 10px',
                                'autofocus': True,
                                'autocomplete': False
                            }
                            
    ), required=False)
    class Meta:
        model = Artist
        fields = ['artistID']

    def clean_id(self, *args, **kwargs):
        clean_id = self.cleaned_data.get("artistID")
        # if not "3" in clean_id: #can do length check or query API 
        #     raise forms.ValidationError("Artist not found")
        # else if ... #for multiple validations
        # else:
        #     return clean_id


class RawerForm(forms.Form):
    artistID       = forms.CharField(label='', widget=forms.TextInput(
                            attrs={
                                "placeholder": "Search"
                            }
                            
    ))