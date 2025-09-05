import psycopg2


def check_if_account_exists_given_id(account_id, cursor: psycopg2.extensions.cursor):
   result = cursor.execute('select id from accounts where id = %s', (account_id,))
   result = cursor.fetchone()
   return result is not None

def check_if_customer_exists_given_id(customer_id, cursor: psycopg2.extensions.cursor):
   result = cursor.execute('select id from customers where id = %s', (customer_id,))
   result = cursor.fetchone()
   return result is not None

