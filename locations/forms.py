from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Div, Field, Fieldset, Layout, Reset, Submit
from crispy_forms.bootstrap import FormActions, Tab, TabHolder

from utils import parser

static_data_parser = parser.CustomParser('static_data.ini')

class ManageLocationForm(forms.Form):

    site = forms.CharField(label='Site', widget=forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    location_id = forms.CharField(
        label='Location ID',
        widget=forms.TextInput(attrs={'readonly':'readonly'}),
        required=False
    )
    location_name = forms.CharField(label='Location', required=True)
    location_latitude = forms.FloatField(label='Latitude (WGS 84)', required=False)
    location_longitude = forms.FloatField(label='Longitude (WGS 84)', required=False)
    location_description = forms.CharField(label='Description', widget=forms.Textarea, max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super(ManageLocationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-manageLocationForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('site'),
            Field('location_id'),
            Field('location_name'),
            Field('location_latitude'),
            Field('location_longitude'),
            Field('location_description'),
            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_id="id-cancelBtn", css_class="btn-default pull-right"),
            )
        )

    def clean_gps_coordinates(self):
        position = None
        location_latitude = self.cleaned_data['location_latitude']
        location_longitude = self.cleaned_data['location_longitude']
        if (location_latitude and location_longitude):
            position = {'location_latitude' : location_latitude,
                        'location_longitude' : location_longitude}
        return position
