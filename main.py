import string
from fastapi import FastAPI

from lib.db_connection import get_db_connection

app = FastAPI()

@app.get("/")
async def read_root():
    return { 'docs': ''}

@app.post("create-customer")
async def create_customer(first: str, last: str, email: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                response = cursor.execute(
                    "INSERT INTO customers (first_name, last_name, email) VALUES (%s, %s, %s) returning *",
                    (first, last, email)
                )
                print(response)
                # TODO: return customer id
                return { 'success': True }
    except Exception as e:
        print(e)
        return {'error': 'Failed to create customer'}, 400

@app.post("create-account")
async def create_account(customer_id: string):
    try:
       with get_db_connection() as conn:
           with conn.cursor() as cursor:
               response = cursor.execute(
                   "INSERT INTO accounts (customer_id) VALUES (%s) returning *",
                   (customer_id,)
               )
               return { 'success': True }, 200
    except Exception as e:
        print(e)
        return {'error': 'Failed to create account'}, 400

@app.get("get-customer-balance")
async def get_customer_balance(customer_id: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                response = cursor.execute(
                    "SELECT SUM(amount) FROM transactions WHERE customer_id = %s",
                    (customer_id,)
                )
                return { 'balance': response.fetchone()[0] }, 200
    except Exception as e:
        print(e)
        return {'error': 'Failed to get customer balance'}, 400

@app.post("create-transaction")
async def create_transaction(customer_id: str, amount: float):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                response = cursor.execute(
                    "INSERT INTO transactions (customer_id, amount) VALUES (%s, %s) returning *",
                    (customer_id, amount)
                )
                return { 'success': True }, 200
    except Exception as e:
        print(e)
        return {'error': 'Failed to create transaction'}, 400




