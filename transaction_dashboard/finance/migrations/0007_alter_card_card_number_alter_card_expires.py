# Generated by Django 5.2.3 on 2025-06-24 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_alter_card_card_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='card_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='card',
            name='expires',
            field=models.CharField(max_length=12),
        ),
    ]
