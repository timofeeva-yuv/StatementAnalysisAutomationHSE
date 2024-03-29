# Generated by Django 4.1.4 on 2023-05-16 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_chartcontainer'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ChartContainer',
        ),
        migrations.AddField(
            model_name='chart',
            name='height',
            field=models.FloatField(default=200),
        ),
        migrations.AddField(
            model_name='chart',
            name='width',
            field=models.FloatField(default=320),
        ),
        migrations.AddField(
            model_name='constant',
            name='height',
            field=models.FloatField(default=200),
        ),
        migrations.AddField(
            model_name='constant',
            name='width',
            field=models.FloatField(default=320),
        ),
    ]
