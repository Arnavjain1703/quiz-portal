# Generated by Django 2.0.6 on 2018-06-08 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='category',
            new_name='category_name',
        ),
    ]