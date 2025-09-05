from typing import List, Dict

import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from lib.check_if_account_exists_given_id import check_if_customer_exists_given_id, check_if_account_exists_given_id
from lib.db_connection import get_db_connection
from lib.helpers import validate_input
from schema.models import Customer, Account, Transaction

app = FastAPI()

@app.get("/")
async def read_root():
    return { 'docs': ''}

class CustomerParams(BaseModel):
    first_name: str
    last_name: str
    email: str

@app.post("/create-customer")
async def create_customer(data: dict) -> Customer:
    customer = validate_input(data, CustomerParams)
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO customers (customer_first, customer_last, customer_email) VALUES (%s, %s, %s) RETURNING *",
                    (customer.first_name, customer.last_name, customer.email)
                )
                result = cursor.fetchone()
                conn.commit()

                if result:
                    return Customer(
                        id=result[0],
                        customer_first=result[1],
                        customer_last=result[2],
                        customer_email=result[3],
                        created_at=result[4]
                    )
                else:
                    raise HTTPException(status_code=400, detail="Failed to create customer")

    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Customer with same email already exists")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to create customer")


class AccountParams(BaseModel):
    balance: float = 0
    customer_id: str

@app.post("/create-account")
async def create_account(data: dict) -> Account:
    account_data = validate_input(data, AccountParams)
    if account_data.balance < 0:
        raise HTTPException(
            status_code=400,
            detail="Account balance cannot be negative"
        )
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                account_exists = check_if_customer_exists_given_id(account_data.customer_id, cursor)
                if not account_exists:
                    raise HTTPException(status_code=400, detail="Customer does not exist")
                cursor.execute(
                   "INSERT INTO accounts (customer_id, balance) VALUES (%s, %s) returning *",
                   (account_data.customer_id, account_data.balance)
                )
                result = cursor.fetchone()
                conn.commit()
                return Account(
                    id=result[0],
                    balance=result[1],
                    customer_id=result[2],
                    created_at=result[3]
                )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to create account")

@app.get("/get-customer-balance/{customer_id:str}")
async def get_customer_balance(customer_id: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                customer_exists = check_if_customer_exists_given_id(customer_id, cursor)
                if not customer_exists:
                    raise HTTPException(status_code=400, detail="Customer does not exist")

                cursor.execute(
                    "SELECT SUM(balance) FROM accounts WHERE customer_id = %s",
                    (customer_id,)
                )

                return { 'customer_id': customer_id, 'balance': cursor.fetchone()[0]}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to get customer balance")

@app.get("/get-account-balance/{account_id:str}")
async def get_account_balance(account_id: str):
   try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if not check_if_account_exists_given_id(account_id, cursor):
                    raise HTTPException(status_code=400, detail="Account does not exist")

                cursor.execute(
                    "SELECT balance FROM accounts WHERE id = %s",
                    (account_id,)
                )
                return {
                    'account_id': account_id,
                    'balance': cursor.fetchone()[0]
                }
   except Exception as e:
       print(e)
       raise HTTPException(status_code=500, detail="Failed to get account balance")


class TransactionParams(BaseModel):
    sender_account_id: str
    receiver_account_id: str
    amount: float

@app.post("/create-transaction")
async def create_transaction(input_data: dict) -> Transaction:
    transaction_data = validate_input(input_data, TransactionParams)
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # First we need to check if the sender account has enough balance and take the money out
                # This needs to happen in one atomic transaction, or else the sender account could have a negative balance
                cursor.execute(
                    'update accounts set balance = balance - %s where id = %s and balance >= %s returning *',
                    (transaction_data.amount, transaction_data.sender_account_id, transaction_data.amount)
                )
                deductFromSenderResponse = cursor.fetchone()
                if deductFromSenderResponse is None:
                    conn.rollback()
                    raise HTTPException(status_code=400, detail="Insufficient funds")
                # We can now safely transfer the money to the receiver
                cursor.execute(
                    'update accounts set balance = balance + %s where id = %s returning *',
                    (transaction_data.amount, transaction_data.receiver_account_id)
                )
                cursor.execute(
                    'insert into transactions (sender_account_id, receiver_account_id, amount) values (%s, %s, %s) returning *',
                    (transaction_data.sender_account_id, transaction_data.receiver_account_id, transaction_data.amount)
                )
                result = cursor.fetchone()
                conn.commit()
                return Transaction(
                    id=result[0],
                    amount=result[1],
                    sender_account_id=result[2],
                    receiver_account_id=result[3],
                    created_at=result[4]
                )
            except HTTPException as e:
                raise e
            except Exception as e:
                conn.rollback()
                print(e)
                raise HTTPException(status_code=500, detail="Failed to execute transaction")

@app.get("/get-transactions/{account_id}")
async def get_transactions(account_id: str) -> Dict[str, List[Transaction]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if not check_if_account_exists_given_id(account_id, cursor):
                    raise HTTPException(status_code=400, detail="Account does not exist")

                cursor.execute(
                    "SELECT * FROM transactions WHERE sender_account_id = %s OR receiver_account_id = %s ORDER BY created_at DESC",
                    (account_id, account_id)
                )
                
                transactions = cursor.fetchall()
                formatted_transactions = []
                for transaction in transactions:
                    transaction_data = Transaction(
                        id=transaction[0],
                        amount=transaction[1],
                        sender_account_id=transaction[2],
                        receiver_account_id=transaction[3],
                        created_at=transaction[4]
                    )
                    formatted_transactions.append(transaction_data)
                return { 'transactions': formatted_transactions }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to get transactions")
