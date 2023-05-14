from django.db import models
from django.conf import settings


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
    chart_labels = models.TextField(blank=True)
    chart_values = models.TextField(blank=True)
