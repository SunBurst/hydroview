from django import forms
from django.core.exceptions import ValidationError
from pytz import all_timezones
from collections import OrderedDict

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Field, Layout, Reset, Div, Submit, Fieldset, MultiField
from crispy_forms.bootstrap import FormActions, Tab, TabHolder

from .validators import validate_file
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
    log_description = forms.CharField(label='Description', widget=forms.Textarea, max_length=255, required=False)

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
        validators=[validate_file],
        required=False
    )

    log_file_line_num = forms.IntegerField(label='Last Inserted Line Number', min_value=1, required=False)
    log_update_is_active = forms.BooleanField(label='Automatic Updating is Active', initial=False, validators=[],required=False)

    TIME_ZONE_CHOICES = ()
    for tz in all_timezones:
        TIME_ZONE_CHOICES = TIME_ZONE_CHOICES + ((tz, tz,),)

    log_time_zone = forms.ChoiceField(label='', choices=TIME_ZONE_CHOICES, required=True)

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
                        Field('log_update_is_active'),
                        css_class="customFieldset",
                    ),
                ),
                Tab(
                    'File Info',
                    Fieldset(
                        'File Info',
                        Field('log_file_path'),
                        Field('log_file_line_num'),
                    ),
                ),
                Tab(
                    'Time Info',
                    Fieldset(
                        'Time Zone',
                        Field('log_time_zone'),
                        css_class="customFieldset"
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
                            'Parameter {0}'.format(i+1),
                            Div(
                                Field('parameter_{0}'.format(i)),
                                Field('reading_type_{0}'.format(i), css_class="readingTypeSelect"),
                                Field('time_format_{0}'.format(i)),
                                css_class="parameterDiv"
                            ),
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
                            'Parameter {0}'.format(num_of_init_fields+1),
                            Div(
                                Field('parameter_{0}'.format(num_of_init_fields)),
                                Field('reading_type_{0}'.format(num_of_init_fields), css_class="readingTypeSelect"),
                                Field('time_format_{0}'.format(num_of_init_fields)),
                                css_class="parameterDiv"
                            ),
                            css_class="customFieldset"
                        ),
                    )
                    num_of_init_fields += 1
            else:
                for param_field in range(self.MAX_LOG_PARAMETERS):
                    self.fields['parameter_{0}'.format(param_field)] = forms.CharField(
                        label='Name',
                        required=False
                    )
                    self.fields['reading_type_{0}'.format(param_field)] = forms.ChoiceField(
                        label='Type',
                        choices=PARAMETER_READING_TYPE_CHOICES,
                        initial='disabled',
                        required=False
                    )
                    self.fields['time_format_{0}'.format(param_field)] = forms.ChoiceField(
                        label='Time ID',
                        choices=TIME_FORMAT_CHOICES,
                        initial='disabled',
                        required=False
                    )
                    self.helper.layout[0][3].append(
                        Fieldset(
                            'Parameter {0}'.format(param_field+1),
                            Div(
                                Field('parameter_{0}'.format(param_field)),
                                Field('reading_type_{0}'.format(param_field), css_class="readingTypeSelect"),
                                Field('time_format_{0}'.format(param_field)),
                                css_class="parameterDiv"
                            ),
                            css_class="customFieldset"
                        ),
                    )
                    #self.helper.layout[0][3].append(Field('reading_type_{0}'.format(param_field)))
                    #self.helper.layout[0][3].append(Field('time_format_{0}'.format(param_field)))
        _init_parameters()

    def clean(self):
        cleaned_data = super(ManageLogUpdateInfoForm, self).clean()
        log_update_is_active = cleaned_data.get('log_update_is_active')
        log_file_path = cleaned_data.get('log_file_path')

        if (log_update_is_active and not log_file_path):
            raise ValidationError("No file path set!")

        for i in range(self.MAX_LOG_PARAMETERS):
            param_field = 'parameter_{0}'.format(i)
            param_reading_type_field = 'reading_type_{0}'.format(i)
            param_time_format_field = 'time_format_{0}'.format(i)
            if not (param_field and param_reading_type_field in cleaned_data):
                raise ValidationError(u"Form error!")
            else:
                param_field_value = cleaned_data[param_field]
                param_reading_type_field_value = cleaned_data[param_reading_type_field]
                param_time_format_field_value = cleaned_data[param_time_format_field]
                if (param_field_value and param_reading_type_field_value == 'disabled'):
                    raise ValidationError(u"Parameter {0} ({1}) reading type unfilled!".format((i+1), param_field_value))
                elif (not param_field_value and param_reading_type_field_value !='disabled'):
                    raise ValidationError(u"Parameter {0} name unfilled!".format((i+1)))
                elif (param_reading_type_field_value == 'time' and param_time_format_field_value =='disabled'):
                    raise ValidationError(u"Parameter {0} ({1}) time format unfilled!".format((i+1), param_field_value))

    def clean_parameters(self):
        log_parameters = []
        log_parameter_reading_types = {}
        log_parameter_time_formats = {}
        for i in range(self.MAX_LOG_PARAMETERS):
            param_field = 'parameter_{0}'.format(i)
            param_reading_type_field = 'reading_type_{0}'.format(i)
            param_time_format_field = 'time_format_{0}'.format(i)
            log_parameter_value = self.cleaned_data[param_field]
            log_parameter_reading_type_value = self.cleaned_data[param_reading_type_field]
            if (log_parameter_value and log_parameter_reading_type_value != 'disabled'):
                log_parameters.append(log_parameter_value)
                log_parameter_reading_types[log_parameter_value] = log_parameter_reading_type_value

                if (log_parameter_reading_type_value == 'time'):
                    log_parameter_reading_type_value = self.cleaned_data[param_time_format_field]
                    log_parameter_time_formats[log_parameter_value] = log_parameter_reading_type_value

        return log_parameters, log_parameter_reading_types, log_parameter_time_formats