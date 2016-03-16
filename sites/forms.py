import os
from datetime import datetime, timedelta, timezone
from django import forms
from django.core.exceptions import ValidationError
from pytz import all_timezones
from collections import OrderedDict
from configparser import ConfigParser, NoSectionError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Div, Field, Fieldset, Layout, Reset, Submit
from crispy_forms.bootstrap import FormActions, Tab, TabHolder

from settings.settings import CONFIG_PATH, TIME_ZONE
from .validators import validate_file_extension
from utils.tools import MiscTools
from utils import timemanager

parser = ConfigParser()
parser.read(os.path.join(CONFIG_PATH, 'static_data.ini'))
if not parser:
    print("Config file not found!")

class ManageLoggerTimeFormatForm(forms.Form):

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
            )
        )

        try:
            self.MAX_TIME_IDS = parser.getint('MAX_VALUES', 'max_time_ids')
            self.TIME_ID_TYPES = OrderedDict()
            for name in parser['LOGGER_TIME_ID_TYPES']:
                self.TIME_ID_TYPES[name] = parser['LOGGER_TIME_ID_TYPES'].get(name)
        except (NoSectionError, TypeError, ValueError) as e:
            print(e)

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
                    label='Time Identifier {0} Type'.format(i + 1),
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
                    label='Time Identifier {0} Type'.format(num_of_init_fields + 1),
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
                    label='Time Identifier {0} Type'.format(time_id_field + 1),
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

    log_file_path = forms.CharField(
        label='Current Log File Path',
        widget=forms.TextInput(),
        validators=[validate_file_extension],
        required=False
    )

    log_file_line_num = forms.IntegerField(label='Last Inserted Line Number', min_value=0, required=False)
    update_is_active = forms.BooleanField(label='Automatic Updating is Active', initial=False, required=False)

    TZ_CHOICES = ()
    for tz in all_timezones:
        TZ_CHOICES = TZ_CHOICES + ((tz, tz,),)

    log_time_zone = forms.ChoiceField(label='Log Time Zone', choices=TZ_CHOICES, required=True)

    def __init__(self, *args, **kwargs):
        init_log_parameters = kwargs.pop('init_log_parameters')
        init_log_reading_types = kwargs.pop('init_log_reading_types')
        init_logger_time_formats = kwargs.pop('init_logger_time_formats')
        init_log_time_ids = kwargs.pop('init_log_time_ids')
        super(ManageLogUpdateInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-manageLogUpdateInfoForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'Update Info',
                    Field('update_is_active'),
                ),
                Tab(
                    'File Info',
                    Field('log_file_path'),
                    Field('log_file_line_num'),
                ),
                Tab(
                    'Time Info',
                    Field('log_time_zone'),
                ),
                Tab(
                    'Parameters',
                ),
            ),
            FormActions(
                Submit('save', 'Save', css_class="btn-primary"),
                Reset('reset', 'Reset', css_class="btn-default"),
                Button('cancel', 'Cancel', css_id="id-cancelBtn", css_class="btn-default pull-right")
            )
        )

        try:
            self.MAX_TIME_IDS = parser.getint('MAX_VALUES', 'max_time_ids')
            self.MAX_LOG_PARAMETERS = parser.getint('MAX_VALUES', 'max_log_parameters')
            self.LOG_PARAMETER_READING_TYPES = OrderedDict()
            for name in parser['LOG_PARAMETER_READING_TYPES']:
                self.LOG_PARAMETER_READING_TYPES[name] = parser['LOG_PARAMETER_READING_TYPES'].get(name)
            self.UPDATE_INTERVAL_CHOICES = OrderedDict()
            for name in parser['LOG_UPDATE_INTERVALS']:
                self.UPDATE_INTERVAL_CHOICES[name] = parser['LOG_UPDATE_INTERVALS'].get(name)
        except (NoSectionError, TypeError, ValueError) as e:
            print(e)

        self.fields['update_interval'] = forms.ChoiceField(
            label='Update Interval',
            choices=self.UPDATE_INTERVAL_CHOICES,
            required=False
        )
        self.helper.layout[0][0].append(Field('update_interval'))
        self.fields['daily_interval'] = forms.TimeField(label='Update Every Day At Hour HH:MM:SS', required=False)
        self.fields['hourly_interval'] = forms.TimeField(label='Update Every Hour At Minute (00:MM:SS)', required=False)
        self.helper.layout[0][0].append(Field('daily_interval'))
        self.helper.layout[0][0].append(Field('hourly_interval'))

        LOGGER_TIME_FORMATS = ()
        if (init_logger_time_formats):
            for logger_time_fmt in init_logger_time_formats:
                logger_time_fmt_id = logger_time_fmt.get('logger_time_format_id')
                logger_time_fmt_name = logger_time_fmt.get('logger_time_format_name')
                logger_time_fmt_description = logger_time_fmt.get('logger_time_format_description')
                if not logger_time_fmt_description:
                    logger_time_fmt_description = "No Info Available."
                logger_time_fmt_name_description = logger_time_fmt_name + " (" + logger_time_fmt_description + ")"
                LOGGER_TIME_FORMATS = LOGGER_TIME_FORMATS + (
                    (logger_time_fmt_id, logger_time_fmt_name_description,),
                )

        self.fields['logger_time_format'] = forms.ChoiceField(
            label='Logger Time Format',
            choices=LOGGER_TIME_FORMATS,
            initial='disabled',
            required=True
        )
        self.fields['logger_time_format_time_ids'] = forms.CharField(
            label='Logger Time Format Identifiers Register',
            widget=forms.TextInput(attrs={'readonly':'readonly'}),
            required=False
        )

        self.helper.layout[0][2].append(Field('logger_time_format', css_id="id-loggerTimeFormatField"))
        self.helper.layout[0][2].append(Field('logger_time_format_time_ids', css_id="id-loggerTimeFormatIdsField"))

        if init_log_time_ids:
            num_of_init_fields = 0
            for i, init_log_time_id_field in enumerate(init_log_time_ids):
                self.fields['log_time_format_time_id_{0}'.format(i)] =  forms.CharField(
                    label='Log Time Identifier {0}'.format(i + 1),
                    initial=init_log_time_id_field,
                    required=False
                )
                self.helper.layout[0][2].append(Field('log_time_format_time_id_{0}'.format(i)))
                num_of_init_fields += 1

            while (num_of_init_fields < self.MAX_TIME_IDS):
                self.fields['log_time_format_time_id_{0}'.format(num_of_init_fields)] = forms.CharField(
                    label='Log Time Identifier {0}'.format(num_of_init_fields + 1),
                    required=False
                    )
                self.helper.layout[0][2].append(Field('log_time_format_time_id_{0}'.format(num_of_init_fields)))
                num_of_init_fields += 1
        else:
            for log_time_id_field in range(self.MAX_TIME_IDS):
                self.fields['log_time_format_time_id_{0}'.format(log_time_id_field)] = forms.CharField(
                    label='Log Time Identifier {0}'.format(log_time_id_field + 1),
                    required=False
                )
                self.helper.layout[0][2].append(Field('log_time_format_time_id_{0}'.format(log_time_id_field)))

        PARAMETER_READING_TYPE_CHOICES = (('disabled', ''),)
        for name, description in self.LOG_PARAMETER_READING_TYPES.items():
            PARAMETER_READING_TYPE_CHOICES = PARAMETER_READING_TYPE_CHOICES + ((name, description,),)

        if (init_log_parameters and init_log_reading_types):
            num_of_init_fields = 0
            for i, init_log_param_field in enumerate(init_log_parameters):
                self.fields['parameter_{0}'.format(i)] =  forms.CharField(
                    label='Parameter {0} Name'.format(i + 1),
                    initial=init_log_param_field,
                    required=False
                )
                init_log_param_type_field = init_log_reading_types.get(init_log_param_field)
                self.fields['reading_type_{0}'.format(i)] = forms.ChoiceField(
                    label='Parameter {0} Type'.format(i + 1),
                    choices=PARAMETER_READING_TYPE_CHOICES,
                    initial=init_log_param_type_field,
                    required=False
                )
                self.helper.layout[0][3].append(Field('parameter_{0}'.format(i)))
                self.helper.layout[0][3].append(Field('reading_type_{0}'.format(i)))
                num_of_init_fields += 1

            while (num_of_init_fields < self.MAX_LOG_PARAMETERS):
                self.fields['parameter_{0}'.format(num_of_init_fields)] = forms.CharField(
                    label='Parameter {0} Name'.format(num_of_init_fields + 1),
                    required=False
                    )
                self.fields['reading_type_{0}'.format(num_of_init_fields)] = forms.ChoiceField(
                    label='Parameter {0} Type'.format(num_of_init_fields + 1),
                    choices=PARAMETER_READING_TYPE_CHOICES,
                    initial='disabled',
                    required=False
                )
                self.helper.layout[0][3].append(Field('parameter_{0}'.format(num_of_init_fields)))
                self.helper.layout[0][3].append(Field('reading_type_{0}'.format(num_of_init_fields)))
                num_of_init_fields += 1
        else:
            for param_field in range(self.MAX_LOG_PARAMETERS):
                self.fields['parameter_{0}'.format(param_field)] = forms.CharField(
                    label='Parameter {0} Name'.format(param_field + 1),
                    required=False
                )
                self.fields['reading_type_{0}'.format(param_field)] = forms.ChoiceField(
                    label='Parameter {0} Type'.format(param_field + 1),
                    choices=PARAMETER_READING_TYPE_CHOICES,
                    initial='disabled',
                    required=False
                )
                self.helper.layout[0][3].append(Field('parameter_{0}'.format(param_field)))
                self.helper.layout[0][3].append(Field('reading_type_{0}'.format(param_field)))

    def get_update_info(self):
        is_active = self.cleaned_data['update_is_active']
        update_interval = self.cleaned_data['update_interval']
        update_info = {
            'log_update_interval' : None,
            'log_next_update' : None
        }
        if (is_active and update_interval):
            tm = timemanager.TimeManager()
            utc_time_now = datetime.utcnow()
            local_time_now_tz = tm.utc_dt_to_local_dt(utc_time_now)
            year_now = local_time_now_tz.year
            month_now = local_time_now_tz.month
            day_now = local_time_now_tz.day
            hour = local_time_now_tz.hour
            if (update_interval == 'daily'):
                time = self.cleaned_data['daily_interval']
                hour = time.hour
            elif (update_interval == 'hourly'):
                time = self.cleaned_data['hourly_interval']
            minute = time.minute
            second = time.second

            temp_time_next_update = datetime(year_now, month_now, day_now, hour, minute, second)
            utc_time_next_update = tm.local_dt_to_utc_dt(temp_time_next_update)

            if (tm.utc_dt_to_utc_dt_tz(datetime.utcnow()) > utc_time_next_update):   #: time candidate has passed.
                if (update_interval == 'daily'):
                    utc_time_next_update += timedelta(days=1)
                elif (update_interval == 'hourly'):
                    utc_time_next_update += timedelta(hours=1)
            update_info['log_update_interval'] = update_interval
            update_info['log_next_update'] = utc_time_next_update
        return update_info

    def clean_parameters(self):
        log_parameters = []
        log_parameter_reading_types = {}
        for i in range(self.MAX_LOG_PARAMETERS):
            param_field = 'parameter_{0}'.format(i)
            param_reading_type_field = 'reading_type_{0}'.format(i)
            if (
                (param_field and param_reading_type_field in self.cleaned_data) and
                    self.cleaned_data[param_field] and
                        (self.cleaned_data[param_reading_type_field] != 'disabled')
            ):
                log_parameter = self.cleaned_data[param_field]
                log_parameter_reading_type = self.cleaned_data[param_reading_type_field]
                log_parameters.append(log_parameter)
                log_parameter_reading_types[log_parameter] = log_parameter_reading_type

        return log_parameters, log_parameter_reading_types

    def clean_time_ids(self):
        time_format_ids_order = []
        for i in range(self.MAX_TIME_IDS):
            time_id_field = 'log_time_format_time_id_{0}'.format(i)
            if (time_id_field in self.cleaned_data and self.cleaned_data[time_id_field]):
                time_id = self.cleaned_data[time_id_field]
                time_format_ids_order.append(time_id)
        return time_format_ids_order