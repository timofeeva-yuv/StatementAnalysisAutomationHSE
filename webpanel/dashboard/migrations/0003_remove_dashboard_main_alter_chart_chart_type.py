# Generated by Django 4.1.4 on 2023-05-13 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_chart_chart_labels_chart_chart_values'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dashboard',
            name='main',
        ),
        migrations.AlterField(
            model_name='chart',
            name='chart_type',
            field=models.CharField(choices=[('distribution-chart.html', 'Distribution bar chart'), ('doughnut-distribution-chart.html', 'Distribution pie chart'), ('bar-chart.html', 'Bar chart'), ('doughnut-chart.html', 'Doughnut chart')], max_length=50),
        ),
    ]
