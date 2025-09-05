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
async def create_account(customer_id: str, initial_balance: float = 0):
    try:
       with get_db_connection() as conn:
           with conn.cursor() as cursor:
               response = cursor.execute(
                   "INSERT INTO accounts (customer_id, balance) VALUES (%s, %s) returning *",
                   (customer_id, initial_balance)
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
                    "SELECT SUM(balance) FROM accounts WHERE customer_id = %s",
                    (customer_id,)
                )
                return { 'balance': response.fetchone()[0] }, 200
    except Exception as e:
        print(e)
        return {'error': 'Failed to get customer balance'}, 400

@app.get("get-account-balance")
async def get_account_balance(account_id: str):
   try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                response = cursor.execute(
                    "SELECT balance FROM accounts WHERE id = %s",
                    (account_id,)
                )
                return { 'balance': response.fetchone()[0] }, 200
   except Exception as e:
       print(e)
       return {'error': 'Failed to get account balance'}, 400


@app.post("create-transaction")
async def create_transaction(sender_account_id: str, receiver_account_id: str, amount: float):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # First we need to check if the sender account has enough balance and take the money out
                # This needs to happen in one atomic transaction, or else the sender account could have a negative balance
                deductFromSender = cursor.execute(
                    'update account set balance = balance - %s where id = %s and balance >= %s returning *',
                    (amount, sender_account_id, amount)
                )
                deductFromSenderResponse = deductFromSender.fetchone()
                if deductFromSender is None:
                    return {'error': 'Sender account does not have enough balance'}, 400
                # We can now safely transfer the money to the receiver
                cursor.execute(
                    'update account set balance = balance + %s where id = %s returning *',
                    (amount, receiver_account_id)
                )
                cursor.execute(
                    'insert into transactions (sender_account_id, receiver_account_id, amount) values (%s, %s, %s)',
                    (sender_account_id, receiver_account_id, amount)
                )
    except Exception as e:
        print(e)
        return {'error': 'Failed to create transaction'}, 400
    return { 'success': True }, 200

@app.get("get-transactions")
async def get_transactions(account_id: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                response = cursor.execute(
                    "SELECT * FROM transactions WHERE sender_account_id = %s OR receiver_account_id = %s",
                    (account_id, account_id)
                )
                return { 'transactions': response.fetchall() }, 200
    except Exception as e:
        print(e)
        return {'error': 'Failed to get transactions'}, 400

@app.post("deposit-money")
async def deposit_money(account_id: str, amount: float):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'update account set balance = balance + %s where id = %s returning *',
                    (amount, account_id)
                )
                return { 'success': True }, 200
    except Exception as e:
        print(e)
        return {'error': 'Failed to deposit money'}, 400

@app.post("withdraw-money")
async def withdraw_money(account_id: str, amount: float):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                result = cursor.execute(
                    'update account set balance = balance - %s where id = %s and balance >= %2 returning *',
                    (amount, account_id, amount)
                )
                result = result.fetchone()
                if result is None:
                    return {'error': 'Insufficient funds'}, 400
                return { 'success': True }, 200
    except Exception as e:
        print(e)
        return {'error': 'Failed to withdraw money'}, 400
