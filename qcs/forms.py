from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Field, Fieldset, Layout, Reset, Submit
from crispy_forms.bootstrap import FormActions

from utils import parser

static_data_parser = parser.CustomParser('static_data.ini')

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