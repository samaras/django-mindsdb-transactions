# Generated by Django 5.2.3 on 2025-06-22 22:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_age', models.IntegerField()),
                ('retirement_age', models.IntegerField()),
                ('birth_year', models.IntegerField()),
                ('birth_month', models.IntegerField()),
                ('gender', models.CharField(max_length=10)),
                ('address', models.TextField()),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('per_capita_income', models.DecimalField(decimal_places=2, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'client',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_brand', models.CharField(choices=[('visa', 'Visa'), ('mastercard', 'Mastercard'), ('amex', 'American Express'), ('discover', 'Discover')], max_length=20)),
                ('card_type', models.CharField(choices=[('credit', 'Credit'), ('debit', 'Debit'), ('prepaid', 'Prepaid')], max_length=10)),
                ('card_number', models.CharField(max_length=19)),
                ('expires', models.DateField()),
                ('cvv', models.CharField(max_length=4)),
                ('has_chip', models.BooleanField(default=True)),
                ('num_cards_issued', models.IntegerField(default=1)),
                ('credit_limit', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='finance.client')),
            ],
            options={
                'db_table': 'cards',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('use_chip', models.BooleanField(default=True)),
                ('merchant_id', models.CharField(max_length=50)),
                ('merchant_city', models.CharField(max_length=100)),
                ('merchant_state', models.CharField(max_length=2)),
                ('zip', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='finance.card')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='finance.client')),
            ],
            options={
                'db_table': 'transactions',
                'ordering': ['-date', 'id'],
            },
        ),
    ]
