from django import forms
from .utils import root_fields, students_fields, all_fields, ultimate_fields_database


class DatabaseRequestForm(forms.Form):
    AVAILABLE_TABLES = (
        ('root', 'Ведомостям'),
        ('students', 'Студентам')
    )
    database_table = forms.ChoiceField(choices=AVAILABLE_TABLES, label='По')
    database_select = forms.MultipleChoiceField(label='Показывать столбцы', choices=all_fields)
    database_filters = forms.CharField(widget=forms.Textarea, label='Дополнительные фильтры', required=False)

    def __init__(self, *args, **kwargs):
        super(DatabaseRequestForm, self).__init__(*args, **kwargs)
        self.fields['database_filters'].widget.attrs.update({'id': 'input-field'})

    def is_valid_choices(self, selected_choices, table_value):
        fields = ultimate_fields_database[table_value]
        for elem in selected_choices:
            if elem not in fields:
                return False
        return True

    def clean(self):
        cleaned_data = super().clean()
        table_value = cleaned_data.get('database_table')
        if table_value == 'root':
            self.fields['database_select'].choices = root_fields
        elif table_value == 'students':
            self.fields['database_select'].choices = students_fields
        else:
            self.fields['database_select'].choices = []

        selected_choices = cleaned_data.get('database_select')
        if not self.is_valid_choices(selected_choices, table_value):
            self.add_error('database_select', 'Invalid choices selected.')

        return cleaned_data
