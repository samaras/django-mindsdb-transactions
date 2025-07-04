# Generated by Django 5.2.3 on 2025-06-24 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_remove_card_created_at_remove_card_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='acct_open_date',
            field=models.CharField(default='01/1970', max_length=8),
        ),
        migrations.AddField(
            model_name='card',
            name='card_on_dark_web',
            field=models.CharField(default='No'),
        ),
        migrations.AddField(
            model_name='card',
            name='year_pin_last_changed',
            field=models.IntegerField(default=2025),
        ),
    ]
