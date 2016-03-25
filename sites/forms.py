from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Field,  Layout, Reset, Submit
from crispy_forms.bootstrap import FormActions

from utils import parser
from utils.validators import validate_wgs84_latitude, validate_wgs84_longitude

class ManageSiteForm(forms.Form):

    site_id = forms.CharField(label='Site ID', widget=forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    site_name = forms.CharField(label='Site', required=True)
    site_latitude = forms.CharField(label='Latitude (WGS 84)', validators=[validate_wgs84_latitude], required=False)
    site_longitude = forms.CharField(label='Longitude (WGS 84)', validators=[validate_wgs84_longitude], required=False)
    site_description = forms.CharField(label='Description', widget=forms.Textarea, max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super(ManageSiteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-manageSiteForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('site_id'),
            Field('site_name'),
            Field('site_latitude'),
            Field('site_longitude'),
            Field('site_description'),
            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_id="id-cancelBtn", css_class="btn-default pull-right"),
            )
        )

    def clean(self):
        cleaned_data = super(ManageSiteForm, self).clean()
        site_latitude = cleaned_data.get('site_latitude')
        site_longitude = cleaned_data.get('site_longitude')
        if (site_latitude and not site_longitude):
            raise ValidationError(u"Site longitude unfilled!")
        if (not site_latitude and site_longitude):
            raise ValidationError(u"Site latitude unfilled!")

    def clean_wgs84_coordinates(self):
        position = None
        site_latitude = self.cleaned_data['site_latitude']
        site_longitude = self.cleaned_data['site_longitude']
        if (site_latitude and site_longitude):
            position = {
                'site_latitude' : site_latitude,
                'site_longitude' : site_longitude
            }
        return position