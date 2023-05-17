from django import forms
from .utils import number_fields


class SelectTypeForm(forms.Form):
    AVAILABLE_TYPES = (
        ('distribution_chart', 'Гистограмма распределения'),
        ('distribution_doughnut_chart', 'Круговая диаграмма распределения'),
        ('constant', 'Число')
    )
    types_dict = dict(AVAILABLE_TYPES)
    chart_type_name = forms.ChoiceField(choices=AVAILABLE_TYPES, label='Тип графика')


class DistributionChartForm(forms.Form):
    AVAILABLE_SOURCES = (
        ('MeanMark', 'Средних оценок'),
        ('MeanPositiveMark', 'Средних ненулевых оценок'),
        ('Mark', 'Всех поставленных оценок')
    )
    AVAILABLE_TABLES = (
        ('root', 'Ведомостям'),
        ('students', 'Студентам')
    )
    AVAILABLE_INTERVALS = (
        ('10', '10-балльная'),
        ('5', '5-балльная'),
    )
    distribution_source = forms.ChoiceField(choices=AVAILABLE_SOURCES, label='Распределение')
    database_table = forms.ChoiceField(choices=AVAILABLE_TABLES, label='По')
    distribution_scale = forms.ChoiceField(choices=AVAILABLE_INTERVALS, label='Шкала')
    database_filters = forms.CharField(widget=forms.Textarea, label='Дополнительные фильтры', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['database_filters'].widget.attrs.update({'id': 'input-field'})


class ConstantForm(forms.Form):
    AVAILABLE_TABLES = (
        ('root', 'Ведомостям'),
        ('students', 'Студентам')
    )
    AVAILABLE_AGGREGATIONS = (
        ('avg', "Среднее значение"),
        ('med', "Медиану"),
        ('max', 'Максимальное значение'),
        ('min', "Минимальное значение"),
        ('std', 'Стандартное отклонение'),
        ('sum', 'Сумму')
    )
    database_table = forms.ChoiceField(choices=AVAILABLE_TABLES, label='По')
    database_select = forms.ChoiceField(choices=number_fields, label='Показать значение')
    aggregation = forms.ChoiceField(choices=AVAILABLE_AGGREGATIONS, label='Вывести')
    database_filters = forms.CharField(widget=forms.Textarea, label='Дополнительные фильтры', required=False)

    def __init__(self, *args, **kwargs):
        super(ConstantForm, self).__init__(*args, **kwargs)
        self.fields['database_filters'].widget.attrs.update({'id': 'input-field'})
