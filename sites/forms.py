from datetime import datetime, timedelta
from django import forms
from pytz import all_timezones

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Div, Field, Fieldset, Layout, Reset, Submit
from crispy_forms.bootstrap import FormActions

from settings.settings import TIME_ZONE

MAX_TIME_FORMATS = 5

class ManageLoggerTypeForm(forms.Form):
    logger_type_name = forms.CharField(label='Logger Type', required=True)
    logger_type_description = forms.CharField(label='Description', widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ManageLoggerTypeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'id-manageLoggerTypeForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Basic Info',
                Field('logger_type_name'),
                Field('logger_type_description'),
            ),
            Fieldset(
                'Supported Time Formats',
            ),
            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_id="id-cancelBtn", css_class="btn-default"),
                Button('delete', 'Delete', css_id="id-deleteBtn", css_class="btn-danger pull-right")
            )
        )
        for i in range(0, MAX_TIME_FORMATS):
            self.fields['logger_time_format_%s' % i] = forms.CharField(
                label='Time Format %s' % (i+1),
                required=False
            )
            self.helper.layout[1].append(
                Field('logger_time_format_%s' % i)
            )


class ManageSiteForm(forms.Form):
    site_name = forms.CharField(label='Site', required=True)
    site_latitude = forms.FloatField(label='Latitude (WGS 84)', required=False)
    site_longitude = forms.FloatField(label='Longitude (WGS 84)', required=False)
    site_description = forms.CharField(label='Description', widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ManageSiteForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'id-manageSiteForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('site_name'),
            Field('site_latitude'),
            Field('site_longitude'),
            Field('site_description'),

            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_id="id-cancelBtn", css_class="btn-default"),
                Button('delete', 'Delete', css_id="id-deleteBtn", css_class="btn-danger pull-right")
            )
        )

    def clean_gps_coordinates(self):
        position = None
        site_latitude = self.cleaned_data['site_latitude']
        site_longitude = self.cleaned_data['site_longitude']
        if (site_latitude and site_longitude):
            position = {'site_latitude' : site_latitude,
                        'site_longitude' : site_longitude}
        return position

class ManageLocationForm(forms.Form):
    site_name = forms.CharField(label='Site', widget=forms.TextInput(attrs={'readonly':'readonly'}), required=True)
    location_name = forms.CharField(label='Location', required=True)
    location_latitude = forms.FloatField(label='Latitude (WGS 84)', required=False)
    location_longitude = forms.FloatField(label='Longitude (WGS 84)', required=False)
    location_description = forms.CharField(label='Description', widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ManageLocationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'id-manageLocationForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('site_name'),
            Field('location_name'),
            Field('location_latitude'),
            Field('location_longitude'),
            Field('location_description'),

            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_class="btn-default"),
                Button('delete', 'Delete', css_class="btn-danger pull-right")
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

class ManageSensorForm(forms.Form):
    location = forms.CharField(label='Location', widget=forms.TextInput(attrs={'readonly':'readonly'}), required=True)
    sensor_num = forms.IntegerField(label='Sensor Number', required=True)
    sensor = forms.CharField(label='Sensor Name', required=True)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=True)
    update_is_active = forms.BooleanField(label='Automatic Update is Active', initial=False, required=False)
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
                Field('update_is_active'),
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
        is_active = self.cleaned_data['update_is_active']
        time = self.cleaned_data['update_interval']
        if(is_active and time):
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