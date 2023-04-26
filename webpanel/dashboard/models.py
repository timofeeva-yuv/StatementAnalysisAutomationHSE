from django.db import models
from django.conf import settings


class Dashboard(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    main = models.BooleanField(default=False)


class Chart(models.Model):
    AVAILABLE_TYPES = (
        ('bar-chart.html', 'Bar chart'),
        ('line-chart.html', 'Line chart'),
        ('scatter-chart.html', 'Scatter chart'),
        ('doughnut-chart.html', 'Doughnut chart'),
    )
    dashboard = models.ForeignKey("Dashboard", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    chart_type = models.CharField(max_length=30, choices=AVAILABLE_TYPES, default='line')
    # TODO: chart_const_params
    chart_labels = models.TextField(blank=True)
    chart_values = models.TextField(blank=True)
