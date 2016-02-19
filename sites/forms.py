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

    time_zone = forms.ChoiceField(label='Sensor Time Zone', choices=(), required=True)
    time_format = forms.ChoiceField(label='Time Format', widget=forms.RadioSelect, choices=(('Timestamp','Timestamp',),('Campbell Format', 'Campbell Format',)))
    time_ids = forms.MultipleChoiceField(label='Time Identifiers', choices=(('Year','Year',),('Julian Day', 'Julian Day',), ('Hour', 'Hour',), ('Minute', 'Minute',)))

    def __init__(self, *args, **kwargs):
        params = kwargs.pop('params')
        time_ids = kwargs.pop('time_ids')
        super(ManageSensorForm, self).__init__(*args, **kwargs)

        self.helper1 = FormHelper()
        self.helper1.form_tag = False
        self.helper1.layout = Layout(
            Field('location'),
            Field('sensor_num'),
            Field('sensor'),
            Field('description')
        )

        self.helper2 = FormHelper()
        self.helper2.form_tag = False
        self.helper2.layout = Layout(
            Field('file_path'),
            Field('file_line_num')
        )

        self.helper3 = FormHelper()
        self.helper3.form_tag = False
        self.helper3.layout = Layout(
            Field('time_format'),
            Field('time_zone')
        )

        self.helper4 = FormHelper()
        self.helper4.form_tag = False
        self.helper4.disable_csrf = True
        self.helper4.layout = Layout()

        CHOICES = ()
        for i, tz in enumerate(all_timezones):
            CHOICES = CHOICES + ((tz, tz,),)

        self.fields['time_zone'] = forms.ChoiceField(choices=CHOICES, initial=TIME_ZONE, required=True)

        temp_ids = ()
        for i, time_id in enumerate(time_ids):
            temp_ids = temp_ids + ((time_id, time_id,),)
            #self.fields['time_id_%s' % i] = forms.CharField(label='Time Identifier %s' % i, initial=time_id)
            #self.helper3.layout.append(Field('time_id_%s' % i))

        self.fields['time_ids'] = forms.MultipleChoiceField(choices=(('Year','Year',),('Julian Day', 'Julian Day',), ('Hour', 'Hour',), ('Minute', 'Minute',)), initial=temp_ids)

        for i, param in enumerate(params):
            self.fields['param_%s' % i] = forms.CharField(label='Parameter %s' % i, initial=param)
            self.helper4.layout.append(Field('param_%s' % i))

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

    def pack_time_ids(self):
        time_ids = []
        temp_dict = {}

        for name, value in self.cleaned_data.items():
            if name.startswith('time_id_'):
                temp_dict[name] = value
                time_ids.append('placeholder')

        for time_id, value in temp_dict.items():
            for i in range(len(temp_dict)):
                if(time_id=='time_id_%s' % i):
                    time_ids.insert(i,value)
                    del(time_ids[i+1])

        return time_ids