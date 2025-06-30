-- Connect MindsDB to your PostgreSQL database
-- Replace 'your_db_name', 'your_db_user', 'your_db_password', 'your_db_host', and 'your_db_port'
-- with the actual values from your Django project's .env file.
CREATE DATABASE finance_db
WITH ENGINE = 'postgres',
PARAMETERS = {
    "host": 'your_db_host',
    "port": 5432,
    "username": 'your_db_user',
    "password": 'your_db_password',
    "database": 'your_db_name';
};

-- ---------------------------------------------------------------------------

-- MindsDB Knowledge Base Setup: Create and Ingest Data

-- 1. Create a Knowledge Base for Client data
-- We will use 'address' and 'gender' as content for semantic search,
-- and include 'per_capita_income', 'current_age', and 'birth_year' as metadata for filtering.
CREATE KNOWLEDGE_BASE client_kb
USING 
    embedding_model = {
        "provider": "gemini",
        "model_name": 'gemini-embedding-exp-03-07',
        "api_key": "xxxxxx"
    },
    reranking_model = {
        "provider": "gemini",
        "model_name": "gemini-pro",
        "api_key": "xxxxxx"
    },
    content_column = 'address',
    metadata_columns = ['per_capita_income', 'current_age', 'gender', 'birth_year'];

-- 2. Create a Knowledge Base for Transaction data
-- We will use 'merchant_city' and 'merchant_state' for semantic search on location,
-- and 'amount', 'use_chip', 'date', and 'client_id' as metadata.
-- Combining columns for more context for the CONTENT_COLUMN (merchant_city, merchant_state)

CREATE KNOWLEDGE_BASE transaction_kb
USING 
    embedding_model = {
        "provider": "gemini",
        "model_name": 'gemini-embedding-exp-03-07',
        "api_key": "xxxxxx"
    },
    reranking_model = {
        "provider": "gemini",
        "model_name": "gemini-pro",
        "api_key": "xxxxxx"
    },
    content_column = ['merchant_city', 'merchant_state'],
    metadata_columns = ['amount', 'use_chip', 'date', 'client_id'];

-- ------------------------------------------------------------------------------

-- Ingest data into the Knowledge Bases

INSERT INTO client_kb SELECT * FROM finance_db.client;
INSERT INTO transaction_kb SELECT * FROM finance_db.transactions;

-- You can verify the data was inserted by querying the Knowledeg Bases:
SELECT count(*) FROM client_kb;
SELECT count(*) FROM transaction_kb;

-- ------------------------------------------------------------------------------

-- Create Indexes on your Knowledge Bases

CREATE INDEX ON client_kb;
CREATE INDEX ON transaction_kb;


-- -------------------------------------------------------------------------------

-- MindsDB Knowledge Base Semantic Queries with Metadata Filtering
-- These commands are what will be run from the django view, they are 
-- included here just for completeness,

-- Find clients in "wealthy, suburban areas" and filter by age and income:
SELECT
    c.id AS client_id,
    c.address,
    c.current_age,
    c.per_capita_income,
    c.gender
FROM
    client_kb AS c
WHERE
    content LIKE 'wealthy, suburban areas' AND 
    c.current_age > 40 AND                    
    c.per_capita_income > 70000;              

-- Find transactions related to "travel expenses" and filter for high amounts and chip usage:
SELECT
    t.id AS transaction_id,
    t.amount,
    t.date,
    t.merchant_city,
    t.merchant_state,
    t.use_chip,
    t.client_id
FROM
    transaction_kb AS t
WHERE
    content LIKE 'travel expenses' AND   
    t.amount > 500 AND                   
    t.use_chip = TRUE;                   

-- Find transactions for "online shopping" in a specific state:
SELECT
    t.id AS transaction_id,
    t.amount,
    t.merchant_city,
    t.merchant_state,
    t.client_id
FROM
    transaction_kb AS t
WHERE
    content LIKE 'online shopping' AND
    t.merchant_state = 'California'; 

-- ------------------------------------------------------------------------------------

-- MindsDB Job for Periodic Knowledge Base Updates

-- This JOB will run every 1 hour (3600 seconds) and check for new transactions
-- in the 'finance_db.finance_transaction' table, inserting them into 'transaction_kb'.

CREATE JOB update_transaction_kb_job (
    INSERT INTO transaction_kb SELECT * FROM finance_db.finance_transactions WHERE date > LAST;
) EVERY 1 HOUR; -- or EVERY 3600 SECONDS;


-- --------------------------------------------------------------------------------------


-- MindsDB AI Table Integration with Knowledge Base Results

-- Create the Gemini handler, or OPENAI if you can afford it :P :
CREATE ML_ENGINE google_gemini_engine
FROM google_gemini
USING
    api_key = 'xxxxxx'; -- Replace with your actual API key


-- Create an AI Table that can summarize text.
-- We will define a custom prompt for summarization.
CREATE ML_MODEL summarize_transactions_model
PREDICT summary
USING
    engine = 'google_gemini_engine', 
    model_name = 'gemini-pro',
    prompt_template = 'Summarize the following transaction details into a concise overview, highlighting key aspects: {{transaction_details}}.';

-- Now, query the Knowledge Base and pipe the results to the AI Table for summarization.
-- Get "suspicious" transactions and summarize them.
-- Semantic search for suspicious transactions
SELECT
    t.id AS transaction_id,
    t.amount,
    t.date,
    t.merchant_city,
    t.merchant_state,
    t.use_chip,
    t.client_id,
    s.summary
FROM
    transaction_kb AS t
JOIN
    summarize_transactions_model AS s
ON
    t.id IS NOT NULL 
WHERE
    t.content LIKE 'suspicious activity' AND 
    s.transaction_details = CONCAT(
        'Transaction ID: ', t.id,
        ', Amount: ', t.amount,
        ', Date: ', t.date,
        ', Merchant: ', t.merchant_city, ', ', t.merchant_state,
        ', Used Chip: ', t.use_chip
    );


-- REFINED EXAMPLE for AI Table Integration:
SELECT
    t.id AS transaction_id,
    t.amount,
    t.date,
    t.merchant_city,
    t.merchant_state,
    t.use_chip,
    t.client_id,
    s.summary
FROM
    transaction_kb AS t
JOIN
    summarize_transactions_model AS s ON 1=1 -- Simple join
WHERE
    t.content LIKE 'unusual large spending' AND -- Semantic search for unusual spending
    s.transaction_details = CONCAT( -- This CONCAT creates the input for the prompt_template's `transaction_details` variable
        'Transaction ID: ', t.id,
        ', Amount: $', t.amount,
        ', Date: ', t.date,
        ', Merchant City: ', t.merchant_city,
        ', Merchant State: ', t.merchant_state,
        ', Used Chip: ', t.use_chip,
        ', Client ID: ', t.client_id
    );

-- This query first semantically searches `transaction_kb` for 'unusual large spending', 
-- and then summarizes the transactiom
