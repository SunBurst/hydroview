from django import forms
from pytz import all_timezones, timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, ButtonHolder, Div, Field, Fieldset, Layout, Reset, Submit
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

    parameters = forms.CharField(label='Sensor Parameters')

    def __init__(self, *args, **kwargs):
        #params = kwargs.pop('params')
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
                css_id = 'basicInfo'
            ),
            Fieldset(
                'File Info',
                Field('file_path'),
                Field('file_line_num'),
                css_id = 'fileInfo'
            ),
            Fieldset(
                'Time Info',
                Field('time_format'),
                Field('time_zone'),
                Field('time_ids'),
                css_id='timeInfo'
            ),
            Fieldset(
                'Parameter Info',
                Field('parameters'),
                css_id='parameterInfo'
            ),
            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_class="btn-default"),
            )
        )

        #for i, param in enumerate(params):
            #self.fields['param_%s' % i] = forms.CharField(label='Parameter %s' % i, initial=param)
            #self.helper.layout[3][1].append(Field('param_%s' % i))

    def cleanTimeIds(self, time_format):
        timeIds = ""
        if (time_format == "timestamp"):
            timeIds = "timestamp"
        elif (time_format == "campbell"):
            timeIds = self.cleaned_data['time_ids']
        return timeIds

    # def pack_parameters(self):
    #    parameters = []
    #    temp_dict = {}

    #    for name, value in self.cleaned_data.items():
    #        print(name,value)
    #        if name.startswith('param_'):
    #            temp_dict[name] = value
    #            parameters.append('placeholder')

    #    for param_id, value in temp_dict.items():
    #        print(param_id, value)
    #        for i in range(len(temp_dict)):
    #            if(param_id == 'param_%s' % i):
    #                parameters.insert(i,value)
    #                del(parameters[i+1])

    #    return parameters