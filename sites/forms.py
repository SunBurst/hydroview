from django import forms

class LocationAddForm(forms.Form):
    name = forms.CharField(required=True)
    latitude = forms.FloatField()
    longitude = forms.FloatField()
    description = forms.CharField(widget=forms.Textarea)

