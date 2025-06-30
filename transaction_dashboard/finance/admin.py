from django.contrib import admin
from .models import Client, Card, Transaction


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'current_age', 'retirement_age', 'gender', 'per_capita_income')
    list_filter = ('gender', 'birth_month', 'current_age')
    search_fields = ('id', 'address')
    ordering = ('id',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('current_age', 'retirement_age', 'birth_year', 'birth_month', 'gender')
        }),
        ('Location', {
            'fields': ('address', 'latitude', 'longitude')
        }),
        ('Financial', {
            'fields': ('per_capita_income',)
        }),
    )


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'card_brand', 'card_type', 'has_chip', 'credit_limit', 'expires')
    list_filter = ('card_brand', 'card_type', 'has_chip', 'expires')
    search_fields = ('id', 'client__id', 'card_number')
    ordering = ('id',)
    
    fieldsets = (
        ('Card Information', {
            'fields': ('client', 'card_brand', 'card_type', 'card_number', 'cvv', 'expires')
        }),
        ('Card Features', {
            'fields': ('has_chip', 'num_cards_issued', 'credit_limit')
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'client', 'card', 'amount', 'merchant_city', 'merchant_state')
    list_filter = ('date', 'use_chip', 'merchant_state', 'card__card_brand')
    search_fields = ('id', 'client__id', 'card__id', 'merchant_id', 'merchant_city')
    ordering = ('-date', 'id')
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('date', 'client', 'card', 'amount', 'use_chip')
        }),
        ('Merchant Information', {
            'fields': ('merchant_id', 'merchant_city', 'merchant_state', 'zip')
        }),
    )
