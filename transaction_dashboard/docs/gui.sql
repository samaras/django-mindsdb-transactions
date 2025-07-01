-- Connect MindsDB to your PostgreSQL database
-- Replace 'your_db_name', 'your_db_user', 'your_db_password', 'your_db_host', and 'your_db_port'
-- with the actual values from your Django project's .env file.
CREATE DATABASE django_db
WITH ENGINE = 'postgres',
PARAMETERS = {
    "host": "your_db_host",
    "port": 5432,
    "user": "your_db_user", 
    "password": "your_db_password",
    "database": "your_db_name"
};

-- Verify the connection
SHOW DATABASES;
-- You should see 'django_db' listed with 'postgres' as the engine.

-- MindsDB Knowledge Base Setup: Create and Ingest Data

-- 1. Create a Knowledge Base for Client data
-- We'll use 'address' as content for semantic search,
-- and include other fields as metadata for filtering.
CREATE KNOWLEDGE_BASE client_kb
USING
    model = 'sentence_transformers',
    embeddings_table = 'client_embeddings';

-- 2. Create a Knowledge Base for Transaction data  
-- We'll use merchant location data for semantic search
CREATE KNOWLEDGE_BASE transaction_kb
USING
    model = 'sentence_transformers',
    embeddings_table = 'transaction_embeddings';

-- 3. Insert data into the Knowledge Bases
-- Insert client data with address as the content to be embedded
INSERT INTO client_kb (content, metadata)
SELECT 
    address as content,
    JSON_OBJECT(
        'id', id,
        'per_capita_income', per_capita_income,
        'current_age', current_age,
        'gender', gender,
        'birth_year', birth_year
    ) as metadata
FROM django_db.core_client;

-- Insert transaction data with merchant location as content
INSERT INTO transaction_kb (content, metadata)
SELECT 
    CONCAT(merchant_city, ', ', merchant_state) as content,
    JSON_OBJECT(
        'id', id,
        'amount', amount,
        'use_chip', use_chip,
        'date', date,
        'client_id', client_id
    ) as metadata
FROM django_db.core_transaction;

-- Verify the data was inserted
SELECT COUNT(*) as client_count FROM client_kb;
SELECT COUNT(*) as transaction_count FROM transaction_kb;

-- MindsDB Knowledge Base Semantic Queries

-- Example 1: Find clients in wealthy suburban areas and filter by age and income
SELECT 
    kb.content,
    JSON_EXTRACT(kb.metadata, '$.id') as client_id,
    JSON_EXTRACT(kb.metadata, '$.current_age') as current_age,
    JSON_EXTRACT(kb.metadata, '$.per_capita_income') as per_capita_income,
    JSON_EXTRACT(kb.metadata, '$.gender') as gender
FROM client_kb kb
WHERE kb.content LIKE 'wealthy suburban areas'
    AND CAST(JSON_EXTRACT(kb.metadata, '$.current_age') AS INT) > 40
    AND CAST(JSON_EXTRACT(kb.metadata, '$.per_capita_income') AS INT) > 70000
ORDER BY kb.distance
LIMIT 10;

-- Example 2: Find transactions in areas related to travel and filter for high amounts
SELECT 
    kb.content as merchant_location,
    JSON_EXTRACT(kb.metadata, '$.id') as transaction_id,
    JSON_EXTRACT(kb.metadata, '$.amount') as amount,
    JSON_EXTRACT(kb.metadata, '$.date') as date,
    JSON_EXTRACT(kb.metadata, '$.use_chip') as use_chip,
    JSON_EXTRACT(kb.metadata, '$.client_id') as client_id
FROM transaction_kb kb
WHERE kb.content LIKE 'airport hotels travel'
    AND CAST(JSON_EXTRACT(kb.metadata, '$.amount') AS DECIMAL) > 500
    AND JSON_EXTRACT(kb.metadata, '$.use_chip') = true
ORDER BY kb.distance
LIMIT 10;

-- Example 3: Find transactions in online shopping areas
SELECT 
    kb.content as merchant_location,
    JSON_EXTRACT(kb.metadata, '$.id') as transaction_id,
    JSON_EXTRACT(kb.metadata, '$.amount') as amount,
    JSON_EXTRACT(kb.metadata, '$.client_id') as client_id
FROM transaction_kb kb  
WHERE kb.content LIKE 'online e-commerce digital'
ORDER BY kb.distance
LIMIT 10;

-- MindsDB Job for Periodic Knowledge Base Updates

-- Create a job to periodically update the transaction knowledge base
-- This will run every hour and add new transactions
CREATE JOB update_transaction_kb_job (
    INSERT INTO transaction_kb (content, metadata)
    SELECT 
        CONCAT(merchant_city, ', ', merchant_state) as content,
        JSON_OBJECT(
            'id', id,
            'amount', amount,
            'use_chip', use_chip,
            'date', date,
            'client_id', client_id
        ) as metadata
    FROM django_db.core_transaction
    WHERE date > (
        SELECT MAX(CAST(JSON_EXTRACT(metadata, '$.date') AS DATETIME)) 
        FROM transaction_kb
    )
) EVERY 1 hour;

-- To view existing jobs
SELECT * FROM information_schema.jobs;

-- MindsDB AI Model Integration

-- Create an ML engine for OpenAI (replace with your API key)
CREATE ML_ENGINE openai_engine
FROM openai
USING
    openai_api_key = 'sk-your-openai-api-key-here';

-- Create a model for transaction analysis
CREATE MODEL transaction_analyzer
PREDICT analysis
USING
    engine = 'openai_engine',
    model_name = 'gpt-3.5-turbo',
    prompt_template = 'Analyze the following transaction data and identify any suspicious patterns or anomalies. Transaction details: {{transaction_details}}. Provide a brief summary of your findings.';

-- Example query combining knowledge base search with AI analysis
SELECT 
    kb.content as location,
    JSON_EXTRACT(kb.metadata, '$.id') as transaction_id,
    JSON_EXTRACT(kb.metadata, '$.amount') as amount,
    JSON_EXTRACT(kb.metadata, '$.date') as date,
    m.analysis
FROM transaction_kb kb
JOIN transaction_analyzer m
WHERE kb.content LIKE 'suspicious unusual activity'
    AND CAST(JSON_EXTRACT(kb.metadata, '$.amount') AS DECIMAL) > 1000
    AND m.transaction_details = CONCAT(
        'ID: ', JSON_EXTRACT(kb.metadata, '$.id'),
        ', Amount: $', JSON_EXTRACT(kb.metadata, '$.amount'),
        ', Date: ', JSON_EXTRACT(kb.metadata, '$.date'),
        ', Location: ', kb.content,
        ', Chip Used: ', JSON_EXTRACT(kb.metadata, '$.use_chip')
    )
ORDER BY kb.distance
LIMIT 5;