from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from decimal import Decimal
from finance.models import Client, Card, Transaction


class Command(BaseCommand):
    help = 'Create sample data for testing the transaction dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clients',
            type=int,
            default=10,
            help='Number of clients to create (default: 10)'
        )
        parser.add_argument(
            '--cards-per-client',
            type=int,
            default=2,
            help='Number of cards per client (default: 2)'
        )
        parser.add_argument(
            '--transactions-per-card',
            type=int,
            default=5,
            help='Number of transactions per card (default: 5)'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Sample data lists
        card_brands = ['visa', 'mastercard', 'amex', 'discover']
        card_types = ['credit', 'debit', 'prepaid']
        genders = ['M', 'F']
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
        states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'FL', 'OH', 'GA', 'NC']
        merchants = ['Walmart', 'Target', 'Amazon', 'Starbucks', 'McDonald\'s', 'Shell', 'CVS', 'Home Depot', 'Best Buy', 'Kroger']
        
        # Create clients
        clients = []
        for i in range(options['clients']):
            birth_year = random.randint(1960, 2000)
            current_age = 2024 - birth_year
            retirement_age = random.randint(60, 70)
            
            client = Client.objects.create(
                current_age=current_age,
                retirement_age=retirement_age,
                birth_year=birth_year,
                birth_month=random.randint(1, 12),
                gender=random.choice(genders),
                address=f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Pine Rd', 'Elm St'])}",
                latitude=Decimal(str(random.uniform(25.0, 49.0))),
                longitude=Decimal(str(random.uniform(-125.0, -66.0))),
                per_capita_income=Decimal(str(random.uniform(20000, 80000)))
            )
            clients.append(client)
        
        self.stdout.write(f'Created {len(clients)} clients')
        
        # Create cards for each client
        cards = []
        for client in clients:
            for j in range(options['cards_per_client']):
                card = Card.objects.create(
                    client=client,
                    card_brand=random.choice(card_brands),
                    card_type=random.choice(card_types),
                    card_number=f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    expires=date.today() + timedelta(days=random.randint(365, 1825)),
                    cvv=str(random.randint(100, 999)),
                    has_chip=random.choice([True, False]),
                    num_cards_issued=random.randint(1, 3),
                    credit_limit=Decimal(str(random.uniform(1000, 50000))) if random.choice(card_types) == 'credit' else None
                )
                cards.append(card)
        
        self.stdout.write(f'Created {len(cards)} cards')
        
        # Create transactions for each card
        transactions = []
        for card in cards:
            for k in range(options['transactions_per_card']):
                transaction_date = timezone.now() - timedelta(days=random.randint(0, 365))
                merchant_city = random.choice(cities)
                merchant_state = random.choice(states)
                
                transaction = Transaction.objects.create(
                    date=transaction_date,
                    client=card.client,
                    card=card,
                    amount=Decimal(str(random.uniform(10, 500))),
                    use_chip=random.choice([True, False]),
                    merchant_id=random.choice(merchants),
                    merchant_city=merchant_city,
                    merchant_state=merchant_state,
                    zip=str(random.randint(10000, 99999))
                )
                transactions.append(transaction)
        
        self.stdout.write(f'Created {len(transactions)} transactions')
        self.stdout.write(self.style.SUCCESS('Sample data creation completed successfully!')) 