# Generated by Django 2.0.6 on 2019-01-23 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20190123_0524'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='university_roll_no',
            field=models.CharField(default='1602710160', max_length=10),
        ),
        migrations.AddField(
            model_name='test',
            name='university_roll_no',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='std_no',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]