from django.db import models
from django.conf import settings


class Dashboard(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class Chart(models.Model):
    AVAILABLE_TYPES = (
        ('distribution-chart.html', 'Distribution bar chart'),
        ('doughnut-distribution-chart.html', 'Distribution pie chart'),
        ('bar-chart.html', 'Bar chart'),
        ('doughnut-chart.html', 'Doughnut chart'),
    )
    dashboard = models.ForeignKey("Dashboard", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    chart_type = models.CharField(max_length=50, choices=AVAILABLE_TYPES)
    # TODO: chart_const_params
    chart_labels = models.TextField(blank=True)
    chart_values = models.TextField(blank=True)
