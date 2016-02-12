from django import forms

class ManageSiteForm(forms.Form):
    site = forms.CharField(label='Site', required=True)
    latitude = forms.FloatField(label='Latitude', required=True)
    longitude = forms.FloatField(label='Longitude', required=True)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=True)