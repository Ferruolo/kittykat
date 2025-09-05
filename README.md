# Banking API

A FastAPI-based banking system that manages customers, accounts, and transactions with PostgreSQL database backend.

## Setup

1. Create and activate virtual environment:
```bash
python -m venv meowenv
source meowenv/bin/activate 
```

2. Install dependencies:
```bash
pip install fastapi uvicorn psycopg2-binary pydantic
```

3. Set up the database:
```bash
# Create database and run schema
psql postgres < schema/schema.sql
```

## How to run
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## How to test
```bash
python tests.py
# to reset database after testing
psql postgres < reset.sql
```

## Endpoints

### Create Customer

- **URL:** `/create-customer`
- **Description:** Create a new customer
- **Parameters:**
  ```json
  {
    "first_name": "string",
    "last_name": "string",
    "email": "string"
  }
  ```

### Create Account

- **URL:** `/create-account`
- **Description:** Create a new account for customer
- **Parameters:**
  ```json
  {
    "balance": "float",
    "customer_id": "string"
  }
  ```

### Get Customer Balance

- **URL:** `/get-customer-balance/{customer_id}`
- **Description:** Get total balance for customer
- **Parameters:**
    - `customer_id`: string (path parameter)

### Get Account Balance

- **URL:** `/get-account-balance/{account_id}`
- **Description:** Get balance for specific account
- **Parameters:**
    - `account_id`: string (path parameter)

### Create Transaction

- **URL:** `/create-transaction`
- **Description:** Create a new transaction between accounts
- **Parameters:**
  ```json
  {
    "sender_account_id": "string",
    "receiver_account_id": "string",
    "amount": "float"
  }
  ```

### Get Transactions

- **URL:** `/get-transactions/{account_id}`
- **Description:** Get all transactions for an account
- **Parameters:**
    - `account_id`: string (path parameter)

