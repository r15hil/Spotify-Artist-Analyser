from django import forms
from .models import Artist

class RawForm(forms.ModelForm):
    artistID       = forms.CharField(label='', widget=forms.TextInput(
                            attrs={
                                "placeholder": "Search"
                            }
                            
    ))
    class Meta:
        model = Artist
        fields = ['artistID']

    def clean_id(self, *args, **kwargs):
        clean_id = self.cleaned_data.get("artistID")
        # if "3" in clean_id: #can do length check etc
        #     return clean_id
        # else:
        #     raise forms.ValidationError("Artist not found")


class RawerForm(forms.Form):
    artistID       = forms.CharField(label='', widget=forms.TextInput(
                            attrs={
                                "placeholder": "Search"
                            }
                            
    ))