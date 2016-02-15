from django import forms

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
    location = forms.CharField(label='Location', required=True)
    sensor_num = forms.IntegerField(label='Sensor Number', required=True)
    sensor = forms.CharField(label='Sensor Name', required=True)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=True)
    file_path = forms.CharField(label='File Path', required=True)
    file_line_num = forms.IntegerField(label='Last Inserted Line Number', required=True)
    time_zone = forms.CharField(label='Time Zone', required=True)

    def __init__(self, *args, **kwargs):
        params = kwargs.pop('params')
        time_ids = kwargs.pop('time_ids')
        super(ManageSensorForm, self).__init__(*args, **kwargs)

        for i, param in enumerate(params):
            self.fields['param_%s' % i] = forms.CharField(label='Parameter %s' % i, initial=param)

        for i, time_id in enumerate(time_ids):
            self.fields['time_id_%s' % i] = forms.CharField(label='Time Identifier %s' % i, initial=time_id)

    def pack_parameters(self):
        parameters = []
        temp_dict = {}

        for name, value in self.cleaned_data.items():
            if name.startswith('param_'):
                temp_dict[name] = value
                parameters.append('placeholder')

        for param_id, value in temp_dict.items():
            for i in range(len(temp_dict)):
                if(param_id=='param_%s' % i):
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