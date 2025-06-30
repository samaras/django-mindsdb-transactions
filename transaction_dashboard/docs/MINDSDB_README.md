# MindsDB Integration with Django

This module provides integration with MindsDB for semantic search and AI-powered analytics using the queries defined in `docs/mindsdb.sql`.

## Setup

### Prerequisites
- MindsDB server running and accessible
- Knowledge bases created and populated (see `docs/mindsdb.sql`)
- Django project with the finance app installed
- Required packages installed (see requirements.txt)

### Installation
1. Ensure MindsDB is running and accessible
2. Run the SQL setup from `docs/mindsdb.sql` to create knowledge bases
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables
Add these to your Django settings or environment:

```python
# In settings.py
MINDSDB_HOST = 'localhost'  # or your MindsDB host
MINDSDB_PORT = 47334        # MindsDB port
MINDSDB_USER = 'mindsdb'    # optional
MINDSDB_PASSWORD = ''       # optional
```

## API Endpoints

### 1. Wealthy Clients Search
```
GET /finance/api/mindsdb/wealthy-clients/
```

**Parameters:**
- `min_age` (optional): Minimum age filter (default: 40)
- `min_income` (optional): Minimum income filter (default: 70000)

**Example:**
```bash
curl "http://localhost:8000/finance/api/mindsdb/wealthy-clients/?min_age=35&min_income=60000"
```

**Response:**
```json
{
  "success": true,
  "query_type": "wealthy_clients",
  "filters": {"min_age": 35, "min_income": 60000},
  "results": [
    {
      "client_id": 123,
      "address": "123 Wealthy St, Suburbia, CA",
      "current_age": 45,
      "per_capita_income": 85000,
      "gender": "M"
    }
  ],
  "count": 1
}
```

### 2. Travel Expenses Search
```
GET /finance/api/mindsdb/travel-expenses/
```

**Parameters:**
- `min_amount` (optional): Minimum transaction amount (default: 500)
- `use_chip` (optional): Filter by chip usage (default: true)

**Example:**
```bash
curl "http://localhost:8000/finance/api/mindsdb/travel-expenses/?min_amount=300&use_chip=true"
```

### 3. Online Shopping Search
```
GET /finance/api/mindsdb/online-shopping/
```

**Parameters:**
- `state` (optional): State filter (default: California)

**Example:**
```bash
curl "http://localhost:8000/finance/api/mindsdb/online-shopping/?state=New%20York"
```

### 4. Suspicious Transactions (with AI Summaries)
```
GET /finance/api/mindsdb/suspicious-transactions/
```

**Example:**
```bash
curl "http://localhost:8000/finance/api/mindsdb/suspicious-transactions/"
```

**Response:**
```json
{
  "success": true,
  "query_type": "suspicious_transactions",
  "results": [
    {
      "transaction_id": 456,
      "amount": 2500.00,
      "date": "2024-01-15T10:30:00Z",
      "merchant_city": "Unknown",
      "merchant_state": "Unknown",
      "use_chip": false,
      "client_id": 123,
      "summary": "This transaction shows unusual patterns: high amount, unknown merchant, and swipe payment method."
    }
  ],
  "count": 1
}
```

### 5. Unusual Spending (with AI Summaries)
```
GET /finance/api/mindsdb/unusual-spending/
```

### 6. Custom Semantic Search
```
GET /finance/api/mindsdb/custom-search/
```

**Parameters:**
- `search_term` (required): Natural language search term
- `kb_type` (optional): Knowledge base type - 'transaction' or 'client' (default: transaction)
- `filter_*` (optional): Any filter parameters (e.g., `filter_amount=1000`)

**Example:**
```bash
curl "http://localhost:8000/finance/api/mindsdb/custom-search/?search_term=high%20value%20purchases&filter_amount=1000"
```

### 7. MindsDB Statistics
```
GET /finance/api/mindsdb/stats/
```

**Response:**
```json
{
  "success": true,
  "connection_status": true,
  "knowledge_base_stats": {
    "client_kb_count": 1000,
    "transaction_kb_count": 5000
  }
}
```

### 8. Execute Custom SQL Query
```
POST /finance/api/mindsdb/execute-query/
```

**Request Body:**
```json
{
  "query": "SELECT * FROM client_kb WHERE content LIKE 'young professionals' LIMIT 10;"
}
```

## Python Usage

### Basic Usage
```python
from finance.mindsdb_util import mindsdb_util

# Test connection
if mindsdb_util.test_connection():
    print("MindsDB is connected!")

# Get knowledge base stats
stats = mindsdb_util.get_knowledge_base_stats()
print(f"Client KB: {stats['client_kb_count']} records")
print(f"Transaction KB: {stats['transaction_kb_count']} records")
```

### Predefined Queries
```python
# Find wealthy clients
wealthy_clients = mindsdb_util.find_wealthy_clients(
    min_age=35, 
    min_income=60000
)

# Find travel expenses
travel_expenses = mindsdb_util.find_travel_expenses(
    min_amount=300, 
    use_chip=True
)

# Find online shopping in specific state
online_shopping = mindsdb_util.find_online_shopping(state='California')

# Find suspicious transactions with AI summaries
suspicious = mindsdb_util.find_suspicious_transactions()

# Find unusual spending with AI summaries
unusual = mindsdb_util.find_unusual_spending()
```

### Custom Semantic Search
```python
# Search transactions
results = mindsdb_util.custom_semantic_search(
    search_term="luxury purchases",
    kb_type="transaction",
    filters={"amount": 1000, "use_chip": True}
)

# Search clients
results = mindsdb_util.custom_semantic_search(
    search_term="tech professionals",
    kb_type="client",
    filters={"current_age": 30}
)
```

### Custom SQL Queries
```python
# Execute any SQL query
query = """
SELECT 
    t.id as transaction_id,
    t.amount,
    t.merchant_city,
    c.current_age
FROM transaction_kb t
JOIN client_kb c ON t.client_id = c.id
WHERE t.amount > 500
LIMIT 10;
"""

results = mindsdb_util.execute_query(query)
```

## Knowledge Base Structure

### Client Knowledge Base (`client_kb`)
- **Content Column**: `address` (for semantic search)
- **Metadata Columns**: `per_capita_income`, `current_age`, `gender`, `birth_year`

### Transaction Knowledge Base (`transaction_kb`)
- **Content Column**: `merchant_city, merchant_state` (for semantic search)
- **Metadata Columns**: `amount`, `use_chip`, `date`, `client_id`

## AI Integration

The system includes AI-powered summarization using Google Gemini:

### AI Model Setup
```sql
-- Create Gemini engine
CREATE ML_ENGINE google_gemini_engine
FROM google_gemini
USING api_key = 'your_api_key';

-- Create summarization model
CREATE ML_MODEL summarize_transactions_model
PREDICT summary
USING
    engine = 'google_gemini_engine', 
    model_name = 'gemini-pro',
    prompt_template = 'Summarize the following transaction details into a concise overview, highlighting key aspects: {{transaction_details}}.';
```

### AI-Enhanced Queries
- `find_suspicious_transactions()`: Returns AI-generated summaries of suspicious transactions
- `find_unusual_spending()`: Returns AI-generated summaries of unusual spending patterns

## Testing

Run the comprehensive test suite:

```bash
cd transaction_dashboard
python finance/test_mindsdb.py
```

The test suite includes:
- Connection testing
- SQL query execution testing
- Custom search testing
- AI integration testing

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Ensure MindsDB server is running
   - Check host/port configuration
   - Verify network connectivity

2. **Knowledge Base Not Found**
   - Run the setup SQL from `docs/mindsdb.sql`
   - Verify knowledge base names match

3. **AI Model Errors**
   - Ensure Google Gemini API key is configured
   - Check if AI models are created in MindsDB

4. **Query Errors**
   - Verify SQL syntax
   - Check if required tables/columns exist
   - Ensure proper permissions

### Debug Mode
Enable debug logging in Django settings:
```python
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'finance.mindsdb_util': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Performance Considerations

- Use appropriate LIMIT clauses in queries
- Consider caching for frequently accessed data
- Monitor query performance with large transactions

