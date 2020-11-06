# Generated by Django 3.1.2 on 2020-11-03 19:52

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import markdownx.models
import uuid


class Migration(migrations.Migration):

    replaces = [('products', '0001_initial'), ('products', '0002_auto_20200830_1458'), ('products', '0003_auto_20200830_1503'), ('products', '0004_program_author'), ('products', '0005_program_featured_image'), ('products', '0006_program_page_content'), ('products', '0007_auto_20200907_1605'), ('products', '0008_auto_20200907_1955'), ('products', '0009_auto_20200908_0037'), ('products', '0010_auto_20200909_1823'), ('products', '0011_program_stripe_price_id')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80, verbose_name='Name of product')),
                ('slug', models.SlugField(default='', max_length=80, unique=True, verbose_name='Slug for product')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='Short description of product')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='Number of times viewed')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Time created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Time last modified')),
                ('program_file', models.FileField(blank=True, null=True, upload_to='', verbose_name='File containing program')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Author of product')),
                ('featured_image', models.ImageField(blank=True, upload_to='products/images/', verbose_name='Featured product image')),
                ('page_content', markdownx.models.MarkdownxField(blank=True, default='', verbose_name='Page content, in markdown')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Price')),
                ('duration', models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Number of weeks')),
                ('frequency', models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Training sessions per week')),
                ('categories', models.ManyToManyField(to='products.Category')),
                ('status', models.CharField(choices=[('pb', 'Public'), ('pr', 'Private'), ('dr', 'Draft')], default='dr', max_length=2)),
                ('stripe_price_id', models.CharField(blank=True, max_length=100, verbose_name='Stripe Price ID')),
            ],
            options={
                'abstract': False,
                'ordering': ['-created'],
            },
        ),
    ]
