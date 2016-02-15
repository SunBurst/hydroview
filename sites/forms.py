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
    file_path = forms.FileField(label='File Path', required=True)
    file_line_num = forms.CharField(label='Last Line Number', required=True)
    parameters = forms.CharField(label='Parameters', widget=forms.Textarea, required=True)
    time_ids = forms.CharField(label='Time Identifiers', widget=forms.Textarea, required=True)
    time_zone = forms.CharField(label='Time Zone', required=True)
