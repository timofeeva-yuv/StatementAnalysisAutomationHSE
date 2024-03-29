# Generated by Django 4.1.4 on 2023-05-13 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_remove_dashboard_main_alter_chart_chart_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='chart',
            name='database_table',
            field=models.CharField(choices=[('root', 'Ведомостям'), ('students', 'Студентам')], default='root', max_length=100),
        ),
        migrations.AddField(
            model_name='chart',
            name='distribution_scale',
            field=models.CharField(choices=[('10', '10-балльная'), ('5', '5-балльная')], default='10', max_length=100),
        ),
        migrations.AddField(
            model_name='chart',
            name='distribution_source',
            field=models.CharField(choices=[('Mark', 'Всех поставленных оценок'), ('MeanMark', 'Средних оценок'), ('MeanPositiveMark', 'Средних ненулевых оценок')], default='Mark', max_length=100),
        ),
        migrations.AlterField(
            model_name='chart',
            name='chart_type',
            field=models.CharField(choices=[('bar-chart.html', 'Гистограмма распределения'), ('doughnut-chart.html', 'Круговая диаграмма распределения')], default='bar-chart.html', max_length=50),
        ),
    ]
