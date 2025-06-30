from django.db import models

# Create your models here.

class Client(models.Model):
    """Client model - separate from Django User model since clients cannot login"""
    current_age = models.IntegerField()
    retirement_age = models.IntegerField()
    birth_year = models.IntegerField()
    birth_month = models.IntegerField()
    gender = models.CharField(max_length=10)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    per_capita_income = models.DecimalField(max_digits=12, decimal_places=2)
    yearly_income = models.DecimalField(max_digits=12, decimal_places=2)
    total_debt = models.DecimalField(max_digits=12, decimal_places=2)
    credit_score = models.IntegerField(default=0)
    num_credit_cards = models.IntegerField(default=0)

    class Meta:
        db_table = 'client'
        ordering = ['id']
    
    def __str__(self):
        return f"Client {self.id}"


class Card(models.Model):
    """Card model linked to clients"""
    CARD_BRAND_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
    ]
    
    CARD_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('prepaid', 'Prepaid'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cards')
    card_brand = models.CharField(max_length=20, choices=CARD_BRAND_CHOICES)
    card_type = models.CharField(max_length=25, choices=CARD_TYPE_CHOICES)
    card_number = models.CharField(max_length=20)  # Masked card number
    expires = models.CharField(max_length=12)
    cvv = models.CharField(max_length=4)  # Should be encrypted in production
    has_chip = models.BooleanField(default=True)
    num_cards_issued = models.IntegerField(default=1)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    acct_open_date = models.CharField(max_length=8, default="01/1970")
    year_pin_last_changed = models.IntegerField(default=2025)
    card_on_dark_web = models.CharField(default="No")
    
    
    class Meta:
        db_table = 'cards'
        ordering = ['id']
    
    def __str__(self):
        return f"Card {self.id} - {self.card_brand} {self.card_type}"


class Transaction(models.Model):
    """Transaction model linked to clients and cards"""

    CHIP_CHOICES = [
        ('chip', 'Chip Transaction'),
        ('swipe', 'Swipe Transaction'),
    ]

    date = models.DateTimeField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='transactions')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    use_chip = models.CharField(default="Chip Transaction", choices=CHIP_CHOICES)
    merchant_id = models.CharField(max_length=50)
    merchant_city = models.CharField(max_length=100)
    merchant_state = models.CharField(max_length=100, null=True, blank=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    mcc = models.IntegerField(default=1000)
    errors = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-date', 'id']
    
    def __str__(self):
        return f"Transaction {self.id} - ${self.amount} on {self.date}"
