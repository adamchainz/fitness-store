# Generated by Django 3.1.2 on 2020-12-04 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='demonstration',
            field=models.URLField(blank=True, default='', verbose_name='Demonstration link'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='explanation',
            field=models.URLField(blank=True, default='', verbose_name='Explanation link'),
        ),
    ]
