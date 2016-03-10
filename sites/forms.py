from datetime import datetime, timedelta
from django import forms
from pytz import all_timezones

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Div, Field, Fieldset, Layout, Reset, Submit
from crispy_forms.bootstrap import FormActions

from settings.settings import TIME_ZONE
from utils.tools import MiscTools

class ManageLoggerTimeFormatForm(forms.Form):
    MAX_TIME_IDS = 5
    TIME_ID_TYPES = {
        'int_year' : 'Integer (Year)',
        'int_julday' : 'Integer (Julian Day)',
        'int_hourminute' : 'Integer (HourMinute)',
        'timetamp' : 'Timestamp (YYYY-MM-DD HH:MM:SS)',
        'timestamp_tz' : 'Timestamp (YYYY-MM-DD HH:MM:SS+ZZZZ)'
    }
    logger_time_format_name = forms.CharField(label='Logger Time Format Name', required=True)
    logger_time_format_description = forms.CharField(label='Description', widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        init_logger_time_ids = kwargs.pop('init_time_ids')
        init_logger_time_id_types = kwargs.pop('init_time_id_types')
        super(ManageLoggerTimeFormatForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-manageLoggerTimeFormatForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Basic Info',
                Field('logger_time_format_name'),
                Field('logger_time_format_description'),
            ),
            Fieldset(
                'Logger Time Identifiers',
            ),
            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_id="id-cancelBtn", css_class="btn-default"),
                Button('delete', 'Delete', css_id="id-deleteBtn", css_class="btn-danger pull-right")
            )
        )

        TIME_ID_TYPE_CHOICES = (('disabled', ''),)
        for name, description in self.TIME_ID_TYPES.items():
            TIME_ID_TYPE_CHOICES = TIME_ID_TYPE_CHOICES + ((name, description,),)

        if (init_logger_time_ids and init_logger_time_id_types):
            num_of_init_fields = 0
            for i, init_time_id_field in enumerate(init_logger_time_ids):
                self.fields['time_format_id_{0}'.format(i)] =  forms.CharField(
                    label='Time Identifier {0}'.format(i + 1),
                    initial=init_time_id_field,
                    required=False
                )
                init_time_id_type_field = init_logger_time_id_types.get(init_time_id_field)
                self.fields['time_format_type_id_{0}'.format(i)] = forms.ChoiceField(
                    label='Time Identifier {0} type'.format(i + 1),
                    choices=TIME_ID_TYPE_CHOICES,
                    initial=init_time_id_type_field,
                    required=False
                )
                self.helper.layout[1].append(Field('time_format_id_{0}'.format(i)))
                self.helper.layout[1].append(Field('time_format_type_id_{0}'.format(i)))
                num_of_init_fields += 1

            while (num_of_init_fields < self.MAX_TIME_IDS):
                self.fields['time_format_id_{0}'.format(num_of_init_fields)] = forms.CharField(
                    label='Time Identifier {0}'.format(num_of_init_fields + 1),
                    required=False
                    )
                self.fields['time_format_type_id_{0}'.format(num_of_init_fields)] = forms.ChoiceField(
                    label='Time Identifier {0} type'.format(num_of_init_fields + 1),
                    choices=TIME_ID_TYPE_CHOICES,
                    initial='inactive',
                    required=False
                )
                self.helper.layout[1].append(Field('time_format_id_{0}'.format(num_of_init_fields)))
                self.helper.layout[1].append(Field('time_format_type_id_{0}'.format(num_of_init_fields)))
                num_of_init_fields += 1
        else:
            for time_id_field in range(self.MAX_TIME_IDS):
                self.fields['time_format_id_{0}'.format(time_id_field)] = forms.CharField(
                    label='Time Identifier {0}'.format(time_id_field + 1),
                    required=False
                )
                self.fields['time_format_type_id_{0}'.format(time_id_field)] = forms.ChoiceField(
                    label='Time Identifier {0} type'.format(time_id_field + 1),
                    choices=TIME_ID_TYPE_CHOICES,
                    initial='inactive',
                    required=False
                )
                self.helper.layout[1].append(Field('time_format_id_{0}'.format(time_id_field)))
                self.helper.layout[1].append(Field('time_format_type_id_{0}'.format(time_id_field)))

    def clean_time_ids(self):
        time_format_id_positions = {}
        time_format_id_types = {}
        for field, value in self.cleaned_data.items():
            for i in range(self.MAX_TIME_IDS):
                if (field == 'time_format_id_{0}'.format(i) and value):
                    time_format_id_positions[i] = value
        for field, value in self.cleaned_data.items():
            for i in range(self.MAX_TIME_IDS):
                if (field == 'time_format_type_id_{0}'.format(i) and i in time_format_id_positions):
                    time_id_name = time_format_id_positions.get(i)
                    time_format_id_types[time_id_name] = value
        time_format_ids_order = [val for key, val in time_format_id_positions.items()]
        return time_format_ids_order, time_format_id_types

class ManageQCForm(forms.Form):
    qc_level = forms.IntegerField(label='Quality Control Level', required=True)
    qc_name = forms.CharField(label='Quality Control Name', required=True)
    qc_description = forms.CharField(label='Description', widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ManageQCForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-manageQCForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Info',
                Field('qc_level'),
                Field('qc_name'),
                Field('qc_description'),
            ),
            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_id="id-cancelBtn", css_class="btn-default"),
                Button('delete', 'Delete', css_id="id-deleteBtn", css_class="btn-danger pull-right")
            )
        )

class ManageSiteForm(forms.Form):
    site_id = forms.CharField(label='Site ID', widget=forms.TextInput(attrs={'readonly':'readonly'}), required=False)
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

    def clean_gps_coordinates(self):
        position = None
        site_latitude = self.cleaned_data['site_latitude']
        site_longitude = self.cleaned_data['site_longitude']
        if (site_latitude and site_longitude):
            position = {'site_latitude' : site_latitude,
                        'site_longitude' : site_longitude}
        return position

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
    location_description = forms.CharField(label='Description', widget=forms.Textarea, required=False)

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

class ManageLogForm(forms.Form):
    location = forms.CharField(
        label='Location', widget=forms.TextInput(attrs={'readonly':'readonly'}), required=False
    )
    log_id = forms.CharField(
        label='Log ID',
        widget=forms.TextInput(attrs={'readonly':'readonly'}),
        required=False
    )
    log_name = forms.CharField(label='Log', required=True)
    log_description = forms.CharField(label='Description', widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ManageLogForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-manageLogForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('location'),
            Field('log_id'),
            Field('log_name'),
            Field('log_description'),

            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_id="id-cancelBtn", css_class="btn-default pull-right"),
            )
        )

class ManageLogUpdateInfoForm(forms.Form):
    update_is_active = forms.BooleanField(label='Automatic Update is Active', initial=False, required=False)
    update_interval = forms.TimeField(label='Update Every Day At', required=False)
    log_file_path = forms.CharField(label='File Path', required=True)
    log_file_line_num = forms.IntegerField(label='Last Inserted Line Number', required=True)

    def __init__(self, *args, **kwargs):
        init_logger_types = kwargs.pop('init_logger_types')
        super(ManageLogUpdateInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-manageLogUpdateInfoForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Logger Type Info',
            ),
            Fieldset(
                'Update Routine',
                Field('update_is_active'),
                Field('update_interval')
            ),
            Fieldset(
                'File Info',
                Field('log_file_path'),
                Field('log_file_line_num'),
            ),
            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_id="id-cancelBtn", css_class="btn-default")
            )
        )

        LOGGER_TYPE_CHOICES = ()

        for logger in init_logger_types:
            for name, time_fmts_dict in logger.items():
                logger_type_name = name
                LOGGER_TYPE_CHOICES = LOGGER_TYPE_CHOICES + ((logger_type_name, logger_type_name,),)
                for time_fmt_label, time_fmts in time_fmts_dict.items():
                    for time_fmt, time_ids in time_fmts.items():
                        LOGGER_TIME_FORMATS = ()
                        LOGGER_TIME_FORMATS = LOGGER_TIME_FORMATS + ((time_fmt, time_fmt,),)
                        print(LOGGER_TIME_FORMATS)
                        self.fields['logger_time_format_%s' % time_fmt] = forms.ChoiceField(
                            label='Logger Time Format',
                            choices=LOGGER_TIME_FORMATS,
                            required=True
                        )
                        LOGGER_TIME_IDS = ()
                        time_ids_str = ", ".join(time_ids)
                        LOGGER_TIME_IDS = LOGGER_TIME_IDS + ((time_fmt, time_ids_str,),)
                        print(LOGGER_TIME_IDS)
                        self.fields['logger_time_ids_%s' % time_fmt] = forms.ChoiceField(
                            label='Logger Time Identifiers',
                            choices=LOGGER_TIME_IDS,
                            required=True
                        )

        self.fields['logger_type_name'] = forms.ChoiceField(
            label='Logger Type',
            choices=LOGGER_TYPE_CHOICES,
            required=True
        )
        self.helper.layout[0].append(
            Field('logger_type_name')
        )

        for name, val in self.fields.items():
            if (name.startswith('logger_time_format_')):
                self.helper.layout[0].append(
                    Field(name)
                )
        for name, val in self.fields.items():
            if (name.startswith('logger_time_ids_')):
                self.helper.layout[0].append(
                    Field(name)
                )

    def get_next_update(self):
        is_active = self.cleaned_data['update_is_active']
        time = self.cleaned_data['update_interval']

        if (is_active and time):
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