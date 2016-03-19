from django import forms
from collections import OrderedDict

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Field, Fieldset, Layout, Reset, Submit
from crispy_forms.bootstrap import FormActions

from utils import parser

static_data_parser = parser.CustomParser('static_data.ini')

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
            self.MAX_TIME_IDS = static_data_parser.getint('GLOBAL_LIMITS', 'max_time_ids')
            self.TIME_ID_TYPES = OrderedDict()
            for name in static_data_parser['LOGGER_TIME_ID_TYPES']:
                self.TIME_ID_TYPES[name] = static_data_parser.get('LOGGER_TIME_ID_TYPES', name)
        except Exception as e:
            print(e)

        TIME_ID_TYPE_CHOICES = (('disabled', '',),)
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