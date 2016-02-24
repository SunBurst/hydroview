from datetime import datetime, timedelta
from django import forms
from pytz import all_timezones

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Field, Fieldset, Layout, Reset, Submit
from crispy_forms.bootstrap import FormActions

from settings.settings import TIME_ZONE

class ManageSiteForm(forms.Form):
    site = forms.CharField(label='Site', required=True)
    latitude = forms.FloatField(label='Latitude', required=False)
    longitude = forms.FloatField(label='Longitude', required=False)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ManageSiteForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'manageSiteForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('site'),
            Field('latitude'),
            Field('longitude'),
            Field('description'),

            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_class="btn-default"),
                Button('delete', 'Delete', css_class="btn-danger pull-right")
            )
        )

    def clean_gps_coordinates(self):
        position = None
        site_latitude = self.cleaned_data['latitude']
        site_longitude = self.cleaned_data['longitude']
        if (site_latitude and site_longitude):
            position = {'latitude' : site_latitude,
                        'longitude' : site_longitude}
        return position

class ManageLocationForm(forms.Form):
    site = forms.CharField(label='Site', widget=forms.TextInput(attrs={'readonly':'readonly'}), required=True)
    location = forms.CharField(label='Location', required=True)
    latitude = forms.FloatField(label='Latitude', required=False)
    longitude = forms.FloatField(label='Longitude', required=False)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ManageLocationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'manageLocationForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('site'),
            Field('location'),
            Field('latitude'),
            Field('longitude'),
            Field('description'),

            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_class="btn-default"),
                Button('delete', 'Delete', css_class="btn-danger pull-right")
            )
        )

    def clean_gps_coordinates(self):
        position = None
        location_latitude = self.cleaned_data['latitude']
        location_longitude = self.cleaned_data['longitude']
        if (location_latitude and location_longitude):
            position = {'latitude' : location_latitude,
                        'longitude' : location_longitude}
        return position

class ManageSensorForm(forms.Form):
    location = forms.CharField(label='Location', widget=forms.TextInput(attrs={'readonly':'readonly'}), required=True)
    sensor_num = forms.IntegerField(label='Sensor Number', required=True)
    sensor = forms.CharField(label='Sensor Name', required=True)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=True)
    update_interval = forms.TimeField(label='Update Every Day At', required=False)
    file_path = forms.CharField(label='File Path', required=True)
    file_line_num = forms.IntegerField(label='Last Inserted Line Number', required=True)
    time_format = forms.ChoiceField(label='Time Format', widget=forms.RadioSelect, choices=(('timestamp','Timestamp',),('campbell', 'Campbell Format',)))

    TZ_CHOICES = ()
    for tz in all_timezones:
        TZ_CHOICES = TZ_CHOICES + ((tz, tz,),)

    time_zone = forms.ChoiceField(label='Sensor Time Zone', choices=TZ_CHOICES, initial=TIME_ZONE, required=True)

    TIME_IDS_CHOICES = (('yearjulianday','Year/Julian Day',),('yearjuliandayhour', 'Year/Julian Day/Hour',), ('yearjuliandayhourminute', 'Year/Julian Day/Hour/Minute',))
    time_ids = forms.ChoiceField(label='Campbell Time Identifiers', choices=TIME_IDS_CHOICES)
    parameters = forms.CharField(label='Sensor Parameters')

    def __init__(self, *args, **kwargs):
        super(ManageSensorForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'manageSensorForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Basic Info',
                Field('location'),
                Field('sensor_num'),
                Field('sensor'),
                Field('description'),
            ),
            Fieldset(
                'Update Routine',
                Field('update_interval')
            ),
            Fieldset(
                'File Info',
                Field('file_path'),
                Field('file_line_num'),
            ),
            Fieldset(
                'Time Info',
                Field('time_format'),
                Field('time_zone'),
                Field('time_ids'),
            ),
            Fieldset(
                'Parameter Info',
                Field('parameters'),
            ),
            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_class="btn-default"),
            )
        )

    def clean_time_ids(self):
        temp_time_format = self.cleaned_data['time_format']
        timeIds = ""
        if (temp_time_format == "timestamp"):
            timeIds = "timestamp"
        elif (temp_time_format == "campbell"):
            timeIds = self.cleaned_data['time_ids']
        return timeIds

    def get_next_update(self):

        time = self.cleaned_data['update_interval']
        if(time):
            hour = time.hour
            minute = time.minute
            second = time.second

            time_now = datetime.now()
            year_now = time_now.year
            month_now = time_now.month
            day_now = time_now.day

            time_next_update = datetime(year_now, month_now, day_now, hour, minute, second)

            if (datetime.now() > time_next_update):   #: time candidate has passed.
                time_next_update += timedelta(days=1)
                return time_next_update
            else:
                return time_next_update
        else:
            return None