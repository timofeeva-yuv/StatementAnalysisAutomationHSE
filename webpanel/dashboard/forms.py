from django.forms import ModelForm, ChoiceField
from .models import Dashboard, Chart


class DashboardForm(ModelForm):
    class Meta:
        model = Dashboard
        fields = ['name']
        labels = {'name': 'Название'}


class ChartForm(ModelForm):
    class Meta:
        model = Chart
        fields = ['name', 'chart_type', 'distribution_source', 'database_table', 'distribution_scale']
        labels = {'name': 'Название',
                  'chart_type': 'Тип графика',
                  'distribution_source': 'Распределение',
                  'database_table': 'По',
                  'distribution_scale': 'Шкала'}


