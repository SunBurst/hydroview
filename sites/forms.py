from django import forms
from pytz import all_timezones, timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Div, Field, Layout, Reset, Submit
from crispy_forms.bootstrap import FormActions

from settings.settings import TIME_ZONE

class ManageSiteForm(forms.Form):
    site = forms.CharField(label='Site', required=True)
    latitude = forms.FloatField(label='Latitude', required=True)
    longitude = forms.FloatField(label='Longitude', required=True)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=True)

class ManageLocationForm(forms.Form):
    site = forms.CharField(label='Site', required=True)
    location = forms.CharField(label='Location', required=True)
    latitude = forms.FloatField(label='Latitude', required=True)
    longitude = forms.FloatField(label='Longitude', required=True)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=True)

class ManageSensorForm(forms.Form):
    location = forms.CharField(label='Location', widget=forms.TextInput(attrs={'readonly':'readonly'}), required=True)
    sensor_num = forms.IntegerField(label='Sensor Number', required=True)
    sensor = forms.CharField(label='Sensor Name', required=True)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=True)

    file_path = forms.CharField(label='File Path', required=True)
    file_line_num = forms.IntegerField(label='Last Inserted Line Number', required=True)

    time_format = forms.ChoiceField(label='Time Format', widget=forms.RadioSelect, choices=(('timestamp','Timestamp',),('campbell', 'Campbell Format',)))

    TZ_CHOICES = ()
    for tz in all_timezones:
        TZ_CHOICES = TZ_CHOICES + ((tz, tz,),)

    time_zone = forms.ChoiceField(label='Sensor Time Zone', choices=TZ_CHOICES, initial=TIME_ZONE, required=True)

    TIME_IDS_CHOICES = (('yearjulianday','Year/Julian Day',),('yearjuliandayhour', 'Year/Julian Day/Hour',), ('yearjuliandayhourminute', 'Year/Julian Day/Hour/Minute',))
    time_ids = forms.ChoiceField(label='Campbell Time Identifiers', choices=TIME_IDS_CHOICES)


    def __init__(self, *args, **kwargs):
        params = kwargs.pop('params')
        super(ManageSensorForm, self).__init__(*args, **kwargs)

        self.helperBasicInfo = FormHelper()
        self.helperBasicInfo.form_tag = False
        self.helperBasicInfo.disable_csrf = False
        self.helperBasicInfo.layout = Layout(
            Field('location'),
            Field('sensor_num'),
            Field('sensor'),
            Field('description')
        )

        self.helperFileInfo = FormHelper()
        self.helperFileInfo.form_tag = False
        self.helperFileInfo.disable_csrf = False
        self.helperFileInfo.layout = Layout(
            Field('file_path'),
            Field('file_line_num')
        )

        self.helperTimeInfo = FormHelper()
        self.helperTimeInfo.form_tag = False
        self.helperTimeInfo.disable_csrf = False
        self.helperTimeInfo.layout = Layout(
            Field('time_format'),
            Field('time_zone'),
            Field('time_ids')
        )

        self.helperParamsInfo = FormHelper()
        self.helperParamsInfo.form_tag = False
        self.helperParamsInfo.disable_csrf = False
        self.helperParamsInfo.layout = Layout(
        )

        for i, param in enumerate(params):
            self.fields['param_%s' % i] = forms.CharField(label='Parameter %s' % i, initial=param)
            self.helperParamsInfo.layout.append(Field('param_%s' % i))


    def pack_parameters(self):
        parameters = []
        temp_dict = {}

        for name, value in self.cleaned_data.items():
            if name.startswith('param_'):
                temp_dict[name] = value
                parameters.append('placeholder')

        for param_id, value in temp_dict.items():
            for i in range(len(temp_dict)):
                if(param_id == 'param_%s' % i):
                    parameters.insert(i,value)
                    del(parameters[i+1])

        return parameters