from django.forms import ModelForm, ChoiceField
from .models import Dashboard, Chart, Constant


class DashboardForm(ModelForm):
    class Meta:
        model = Dashboard
        fields = ['name']
        labels = {'name': 'Название'}


class ChartForm(ModelForm):
    class Meta:
        model = Chart
        fields = ['name', 'chart_type', 'distribution_source', 'database_table', 'distribution_scale',
                  'database_filters']
        labels = {'name': 'Название',
                  'chart_type': 'Тип графика',
                  'distribution_source': 'Распределение',
                  'database_table': 'По',
                  'distribution_scale': 'Шкала',
                  'database_filters': 'Дополнительные фильтры'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['database_filters'].widget.attrs.update({'id': 'input-field'})


class ConstantForm(ModelForm):
    class Meta:
        model = Constant
        fields = ['name', 'database_table', 'database_select', 'aggregation', 'database_filters']
        labels = {
            'name': 'Название',
            'database_table': 'По',
            'database_select': 'Показать значение',
            'aggregation': 'Вывести',
            'database_filters': 'Дополнительные фильтры'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['database_filters'].widget.attrs.update({'id': 'input-field'})
