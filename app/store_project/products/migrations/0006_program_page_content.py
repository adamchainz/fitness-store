# Generated by Django 3.1 on 2020-09-01 15:02

from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_program_featured_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='page_content',
            field=markdownx.models.MarkdownxField(default='', verbose_name='Page content, in markdown'),
        ),
    ]