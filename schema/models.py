from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class Customer(BaseModel):
    id: UUID
    customer_first: str
    customer_last: str
    customer_email: str
    created_at: datetime


class Account(BaseModel):
    id: UUID
    balance: Decimal
    customer_id: UUID
    created_at: datetime


class Transaction(BaseModel):
    id: UUID
    amount: Decimal
    sender_account_id: UUID
    receiver_account_id: UUID
    created_at: datetime
