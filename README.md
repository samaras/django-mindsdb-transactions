# Django Transaction Dashboard

A Django application for managing financial transactions, clients, and cards with PostgreSQL database support.

## Features

- **Client Management**: Store client information including demographics, location, and income
- **Card Management**: Track credit/debit cards with brand, type, and security features
- **Transaction Tracking**: Monitor all financial transactions with merchant details
- **Admin Interface**: Full Django admin interface for data management
- **API Endpoints**: RESTful API endpoints for data access
- **Dashboard**: Web-based dashboard with statistics and recent transactions
- **MindsDB Dashboard**: Web-based dashboard with semantic searches and MindsDB status

## Database Schema

### Client Table
- `id` (Primary Key)
- `current_age` (Integer)
- `retirement_age` (Integer)
- `birth_year` (Integer)
- `birth_month` (Integer)
- `gender` (CharField)
- `address` (TextField)
- `latitude` (DecimalField)
- `longitude` (DecimalField)
- `per_capita_income` (DecimalField)

### Cards Table
- `id` (Primary Key)
- `client_id` (ForeignKey to Client)
- `card_brand` (CharField - Visa, Mastercard, etc.)
- `card_type` (CharField - Credit, Debit, Prepaid)
- `card_number` (CharField)
- `expires` (CharField)
- `cvv` (CharField)
- `has_chip` (BooleanField)
- `num_cards_issued` (IntegerField)
- `credit_limit` (DecimalField)

### Transactions Table
- `id` (Primary Key)
- `date` (DateTimeField)
- `client_id` (ForeignKey to Client)
- `card_id` (ForeignKey to Card)
- `amount` (DecimalField)
- `use_chip` (BooleanField)
- `merchant_id` (CharField)
- `merchant_city` (CharField)
- `merchant_state` (CharField)
- `zip` (CharField)

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/samaras/django-mindsdb-transactions.git
   cd django-mindsdb-transactions
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the `transaction_dashboard` directory:
   ```env
   # Django Settings
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database Settings
   DB_NAME=your_dbname
   DB_USER=your_dbuser
   DB_PASSWORD=your_dbpassword
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. **Set up PostgreSQL database**
   ```sql
   CREATE DATABASE your_dbname;
   CREATE USER your_dbuser WITH PASSWORD 'your_dbpassword';
   GRANT ALL PRIVILEGES ON DATABASE your_dbname TO your_dbuser;
   ALTER DATABASE your_dbname OWNER TO your_dbuser;
   ```

6. **Run migrations**
   ```bash
   cd transaction_dashboard
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Usage

### Web Interface

- **Dashboard**: Visit `http://localhost:8000/` for the main dashboard
- **Admin Panel**: Visit `http://localhost:8000/admin/` for data management

### API Endpoints

- **Clients**: `GET /api/clients/`
- **Cards**: `GET /api/cards/`
- **Transactions**: `GET /api/transactions/`

### Example API Usage

```bash
# Get all clients
curl http://localhost:8000/api/clients/

# Get all cards
curl http://localhost:8000/api/cards/

# Get all transactions
curl http://localhost:8000/api/transactions/
```

## Security Notes

- **CVV Storage**: CVV values are stored as plain text in this demo. In production, implement proper encryption.
- **Card Numbers**: Consider masking card numbers in the database for security.

## Development

### The Kaggle Dataset 

Download the dataset from the Financial Transactions Dataset: Analytics from Kaggle, specifically targeting only 3 files needed for the table models above. They are the Transaction data (`transactions_data.csv`),  Card information( `cards_data.csv`) and the Users data(`users_data`) which is renamed client for our Django app to avoid confusion with the django auth_user. Please note the transactions_data file is massive and will need to be split into 3 or more files for easier handling. You can find a script online to split it up.

Kaggle URL: `https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets`

After downloading the files we will copy them into the database by using the copy command in `psql`. Start with client data(users_data.csv), followed by card data, and finally transaction data(as it has card & client foreign keys). 

Log into psql: 
```sql
\connect your_dbname;

\copy client(id,current_age,retirement_age,birth_year,birth_month,gender,address,latitude,longitude,per_capita_income,yearly_income,total_debt,credit_score,num_credit_cards) FROM '/tmp/users_data.csv' DELIMITER ',' CSV header;
     
\copy cards(id, client_id, card_brand, card_type, card_number, expires, cvv, has_chip, num_cards_issued, credit_limit, acct_open_date, year_pin_last_changed, card_on_dark_web) FROM '/tmp/cards_data.csv' DELIMITER ',' CSV header;

\copy transactions(id, date,client_id, card_id, amount,use_chip,merchant_id, merchant_city, merchant_state, zip, mcc, errors) '/tmp/transaction_data.csv' DELIMITER ',' CSV header;
```

### Connecting MindsDB to PostgreSQL

We are going to run MindsDB locally instead of using the cloud version. You will need *docker* installed. To run MindsDB Web Studio locally execute the following:

```bash
docker run --network=host -p 47334:47334 -p 47335:47335 mindsdb/mindsdb
```

The first step in MindsDB is to connect it to our existing PostgreSQL database. This allows MindsDB to access the **Client**, **Card**, and **Transaction** tables. I ran this command directly in the MindsDB Web Studio:

```sql
CREATE DATABASE finance_db
WITH ENGINE = 'postgres',
PARAMETERS = {
  "host": "localhost",
  "port": 5432,
  "user": "your_user",
  "password": "your_password",
  "database": "your_postgresdb"
};
```  

This creates a virtual database finance _db inside MindsDB, mirroring our PostgreSQL schema. Follow the rest of the sql commands from the docs/mindsdb.sql file. Obviously skip the CREATE DATABASE you just ran above.

### Project Structure

```
transaction_dashboard/
├── finance/                 # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── mindsdb_util.py     # MindsDB interface
│   ├── test_mindsdb.py     # Script to test mindsdb programatically
│   ├── admin.py            # Admin interface
│   ├── urls.py             # URL routing
│   └── templates/
├── docs/                   # MindsDB SQL
│   ├── mindsdb.sql         # SQL file for MindsDB
├── transaction_dashboard/   # Django project settings
│   ├── settings.py         # Django settings
│   └── urls.py             # Main URL configuration
└── manage.py               # Django management script
```



### Adding New Features

1. **Models**: Add new models in `finance/models.py`
2. **Views**: Create views in `finance/views.py`
3. **URLs**: Add URL patterns in `finance/urls.py`
4. **Templates**: Create templates in `finance/templates/finance/`
5. **Admin**: Register models in `finance/admin.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.