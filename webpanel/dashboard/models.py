from django.db import models
from django.conf import settings
from .utils import number_fields


class Dashboard(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class Chart(models.Model):
    AVAILABLE_SOURCES = (
        ('Mark', 'Всех поставленных оценок'),
        ('MeanMark', 'Средних оценок'),
        ('MeanPositiveMark', 'Средних ненулевых оценок'),
    )
    AVAILABLE_TABLES = (
        ('root', 'Ведомостям'),
        ('students', 'Студентам')
    )
    AVAILABLE_INTERVALS = (
        ('10', '10-балльная'),
        ('5', '5-балльная'),
    )
    AVAILABLE_TYPES = (
        ('bar-chart.html', 'Гистограмма распределения'),
        ('doughnut-chart.html', 'Круговая диаграмма распределения'),
    )
    dashboard = models.ForeignKey("Dashboard", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    chart_type = models.CharField(max_length=50, choices=AVAILABLE_TYPES, default='bar-chart.html')
    distribution_source = models.CharField(max_length=100, choices=AVAILABLE_SOURCES, default='Mark')
    database_table = models.CharField(max_length=100, choices=AVAILABLE_TABLES, default='root')
    distribution_scale = models.CharField(max_length=100, choices=AVAILABLE_INTERVALS, default='10')
    database_filters = models.TextField(blank=True)
    chart_labels = models.TextField(blank=True)
    chart_values = models.TextField(blank=True)
    height = models.FloatField(default=200)
    width = models.FloatField(default=320)
    left = models.FloatField(default=0)
    top = models.FloatField(default=0)
    div_type = "chart"


class Constant(models.Model):
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
    dashboard = models.ForeignKey("Dashboard", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    chart_type = "constant.html"
    database_table = models.CharField(choices=AVAILABLE_TABLES, max_length=100, default='root')
    database_select = models.CharField(choices=number_fields, max_length=100, default='MeanMark')
    aggregation = models.CharField(choices=AVAILABLE_AGGREGATIONS, max_length=100, default='avg')
    database_filters = models.TextField(blank=True)
    value = models.TextField(blank=True)
    height = models.FloatField(default=200)
    width = models.FloatField(default=320)
    left = models.FloatField(default=0)
    top = models.FloatField(default=0)
    div_type = "constant"
