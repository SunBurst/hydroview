from datetime import datetime, time, timedelta
from django import forms
from pytz import all_timezones
from collections import OrderedDict

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Field, Layout, Reset, Div, Submit, Row, HTML, Fieldset
from crispy_forms.bootstrap import FormActions, Tab, TabHolder

from .validators import validate_file_extension
from utils import parser, timemanager

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
        init_log_time_formats = kwargs.pop('init_log_time_formats')
        super(ManageLogUpdateInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-manageLogUpdateInfoForm'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'Update Info',
                    Fieldset(
                        'Status',
                        Field('update_is_active'),
                        css_class="customFieldset",
                    ),
                ),
                Tab(
                    'File Info',
                    Field('log_file_path'),
                    Field('log_file_line_num'),
                ),
                Tab(
                    'Time Info',
                    Fieldset(
                        'Time Zone',
                        Field('log_time_zone'),
                    ),
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
        static_data_parser = parser.CustomParser('static_data.ini')
        self.MAX_LOG_PARAMETERS = static_data_parser.getint('GLOBAL_LIMITS', 'max_log_parameters')
        self.LOG_PARAMETER_READING_TYPES = OrderedDict()
        for name in static_data_parser['LOG_PARAMETER_READING_TYPES']:
            self.LOG_PARAMETER_READING_TYPES[name] = static_data_parser.safe_get(
                'LOG_PARAMETER_READING_TYPES', name
            )

        self.LOG_TIME_FORMATS = timemanager.TIME_FORMATS

        def _init_update_interval():
            self.LOG_UPDATE_INTERVALS = OrderedDict()
            for name in static_data_parser['LOG_UPDATE_INTERVALS']:
                self.LOG_UPDATE_INTERVALS[name] = static_data_parser.safe_get('LOG_UPDATE_INTERVALS', name)

            UPDATE_INTERVAL_CHOICES = ()
            for id, name in self.LOG_UPDATE_INTERVALS.items():
                UPDATE_INTERVAL_CHOICES = UPDATE_INTERVAL_CHOICES + ((id, name,),)

            self.fields['update_interval'] = forms.ChoiceField(
                label="",
                choices=UPDATE_INTERVAL_CHOICES,
                required=False
            )

            UPDATE_HOURS_CHOICES = ()
            for i in range(24):
                UPDATE_HOURS_CHOICES = UPDATE_HOURS_CHOICES + ((i, time(i).strftime('%H:%M'),),)

            self.fields['update_at_time'] = forms.ChoiceField(
                label='Update At Hour',
                choices=UPDATE_HOURS_CHOICES,
                required=False
            )

            self.helper.layout[0][0].append(
                Fieldset(
                    'Update Interval',
                    Div(
                        Field('update_interval'),
                    ),
                    Div(
                        Field('update_at_time'),
                    ),
                    css_id="id-updateIntervalFieldset",
                    css_class="customFieldset"
                ),
            )

        def _init_parameters():
            PARAMETER_READING_TYPE_CHOICES = (('disabled', ''),)
            for name, description in self.LOG_PARAMETER_READING_TYPES.items():
                PARAMETER_READING_TYPE_CHOICES = PARAMETER_READING_TYPE_CHOICES + ((name, description,),)

            TIME_FORMAT_CHOICES = (('disabled', ''),)
            for name, description in self.LOG_TIME_FORMATS.items():
                TIME_FORMAT_CHOICES = TIME_FORMAT_CHOICES + ((name, description,),)

            if (init_log_parameters and init_log_reading_types):
                num_of_init_fields = 0
                for i, init_log_param_field in enumerate(init_log_parameters):
                    self.fields['parameter_{0}'.format(i)] =  forms.CharField(
                        label='Name'.format(i+1),
                        initial=init_log_param_field,
                        required=False
                    )
                    init_log_param_type_field = init_log_reading_types.get(init_log_param_field)
                    self.fields['reading_type_{0}'.format(i)] = forms.ChoiceField(
                        label='Type'.format(i+1),
                        choices=PARAMETER_READING_TYPE_CHOICES,
                        initial=init_log_param_type_field,
                        required=False
                    )
                    init_log_param_time_fmt = init_log_time_formats.get(init_log_param_field)
                    self.fields['time_format_{0}'.format(i)] = forms.ChoiceField(
                        label='Time ID'.format(i+1),
                        choices=TIME_FORMAT_CHOICES,
                        initial=init_log_param_time_fmt,
                        required=False
                    )
                    self.helper.layout[0][3].append(
                        Fieldset(
                            'Parameter (Position {0})'.format(i+1),
                            Field('parameter_{0}'.format(i)),
                            Field('reading_type_{0}'.format(i)),
                            Field('time_format_{0}'.format(i)),
                            css_class="customFieldset"
                        ),
                    )
                    num_of_init_fields += 1

                while (num_of_init_fields < self.MAX_LOG_PARAMETERS):   #: Fill up rest of parameters.
                    self.fields['parameter_{0}'.format(num_of_init_fields)] = forms.CharField(
                        label='Name'.format(num_of_init_fields+1),
                        required=False
                        )
                    self.fields['reading_type_{0}'.format(num_of_init_fields)] = forms.ChoiceField(
                        label='Type'.format(num_of_init_fields+1),
                        choices=PARAMETER_READING_TYPE_CHOICES,
                        initial='disabled',
                        required=False
                    )
                    self.fields['time_format_{0}'.format(num_of_init_fields)] = forms.ChoiceField(
                        label='Time ID'.format(num_of_init_fields+1),
                        choices=TIME_FORMAT_CHOICES,
                        initial='disabled',
                        required=False
                    )

                    self.helper.layout[0][3].append(
                        Fieldset(
                            'Parameter (Position {0})'.format(num_of_init_fields+1),
                            Field('parameter_{0}'.format(num_of_init_fields)),
                            Field('reading_type_{0}'.format(num_of_init_fields)),
                            Field('time_format_{0}'.format(num_of_init_fields)),
                            css_class="customFieldset"
                        ),
                    )
                    num_of_init_fields += 1
            else:
                for param_field in range(self.MAX_LOG_PARAMETERS):
                    self.fields['parameter_{0}'.format(param_field)] = forms.CharField(
                        label='Name'.format(param_field+1),
                        required=False
                    )
                    self.fields['reading_type_{0}'.format(param_field)] = forms.ChoiceField(
                        label='Type'.format(param_field+1),
                        choices=PARAMETER_READING_TYPE_CHOICES,
                        initial='disabled',
                        required=False
                    )
                    self.fields['time_format_{0}'.format(param_field)] = forms.ChoiceField(
                        label='Time ID'.format(param_field+1),
                        choices=TIME_FORMAT_CHOICES,
                        initial='disabled',
                        required=False
                    )
                    self.helper.layout[0][3].append(
                        Fieldset(
                            'Parameter (Position {0})'.format(param_field+1),
                            Field('parameter_{0}'.format(param_field)),
                            Field('reading_type_{0}'.format(param_field)),
                            Field('time_format_{0}'.format(param_field)),
                            css_class="customFieldset"
                        ),
                    )
                    #self.helper.layout[0][3].append(Field('reading_type_{0}'.format(param_field)))
                    #self.helper.layout[0][3].append(Field('time_format_{0}'.format(param_field)))

        _init_update_interval()
        _init_parameters()

    def get_update_info(self):
        is_active = self.cleaned_data['update_is_active']
        update_interval_id = self.cleaned_data['update_interval']
        update_info = {
            'log_update_interval' : None,
            'log_next_update' : None
        }
        if (is_active and update_interval_id):
            update_interval = self.LOG_UPDATE_INTERVALS.get(update_interval_id)
            tm = timemanager.TimeManager()
            utc_time_now = datetime.utcnow()
            local_time_now_tz = tm.utc_dt_to_local_dt(utc_time_now)
            year_now = local_time_now_tz.year
            month_now = local_time_now_tz.month
            day_now = local_time_now_tz.day
            hour_choice = int(self.cleaned_data['update_at_time'])
            time_choice = time(hour_choice)
            minute_choice = time_choice.minute
            second_choice = time_choice.second

            temp_time_next_update = datetime(year_now, month_now, day_now, hour_choice, minute_choice, second_choice)
            utc_time_next_update = tm.local_dt_to_utc_dt(temp_time_next_update)

            if (tm.utc_dt_to_utc_dt_tz(datetime.utcnow()) > utc_time_next_update):   #: time candidate has passed.
                if (update_interval_id == 'daily'):
                    utc_time_next_update += timedelta(days=1)
                elif (update_interval_id == 'hourly'):
                    while(tm.utc_dt_to_utc_dt_tz(datetime.utcnow()) > utc_time_next_update):
                        utc_time_next_update += timedelta(hours=1)
            log_update_interval = {
                'log_update_interval_id' : update_interval_id,
                'log_update_interval' : update_interval,
            }
            update_info['log_update_interval'] = log_update_interval
            update_info['log_next_update'] = utc_time_next_update
        return update_info

    def clean_parameters(self):
        log_parameters = []
        log_parameter_reading_types = {}
        log_parameter_time_format = {}
        for i in range(self.MAX_LOG_PARAMETERS):
            param_field = 'parameter_{0}'.format(i)
            param_reading_type_field = 'reading_type_{0}'.format(i)
            param_time_format_field = 'time_format_{0}'.format(i)
            if (
                (param_field and param_reading_type_field in self.cleaned_data) and
                    self.cleaned_data[param_field] and
                        (self.cleaned_data[param_reading_type_field] != 'disabled')
            ):
                log_parameter = self.cleaned_data[param_field]
                log_parameter_reading_type = self.cleaned_data[param_reading_type_field]
                log_parameters.append(log_parameter)
                log_parameter_reading_types[log_parameter] = log_parameter_reading_type
                if (log_parameter_reading_type == 'time' and self.cleaned_data[param_time_format_field] != 'disabled'):
                    log_parameter_time_format[log_parameter] = self.cleaned_data[param_time_format_field]

        return log_parameters, log_parameter_reading_types, log_parameter_time_format