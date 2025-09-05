import requests
import json
import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s'
)

# Not super familar with proper python unit testing
# Building a simple script to create
url = 'http://localhost:8000'

## test 1 - create a new user
user_data_response = requests.post(f'{url}/create-customer',
                                   data=json.dumps({
                                       'first_name': 'Andrew',
                                       'last_name': 'Ferruolo',
                                       'email': 'andrew.ferruolo@gmail.com'}),
                                   headers={'Content-Type': 'application/json'}
                                   )
user_data = user_data_response.json()
user_data_response.raise_for_status()
print("Created user:", user_data)

## test 2 - create a new account for that user
account_1_response = requests.post(f'{url}/create-account', json.dumps({
    'balance': 500,
    'customer_id': user_data['id']
}),
                                   headers={'Content-Type': 'application/json'}
                                   )
account_1_data = account_1_response.json()
print("Created account 1:", account_1_data)

account_2_response = requests.post(f'{url}/create-account', json.dumps({
    'balance': 750,
    'customer_id': user_data['id']
}), headers={'Content-Type': 'application/json'})
account_2_data = account_2_response.json()
print("Created account 2:", account_2_data)

initial_customer_balance = requests.get(f'{url}/get-customer-balance/{user_data["id"]}').json()
print("Initial customer balance:", initial_customer_balance)

initial_account_1_balance = requests.get(f'{url}/get-account-balance/{account_1_data["id"]}').json()
print("Initial account 1 balance:", initial_account_1_balance)

initial_account_2_balance = requests.get(f'{url}/get-account-balance/{account_2_data["id"]}').json()
print("Initial account 2 balance:", initial_account_2_balance)

initial_transaction_history_account_1 = requests.get(f'{url}/get-transactions/{account_1_data["id"]}').json()
print("Initial transaction history account 1:", initial_transaction_history_account_1)

initial_transaction_history_account_2 = requests.get(f'{url}/get-transactions/{account_2_data["id"]}').json()
print("Initial transaction history account 2:", initial_transaction_history_account_2)

# Send 250 from account 1 to account 2 - Do this one the easy way
transaction_1 = requests.post(f'{url}/create-transaction',
                              json.dumps({
                                  'sender_account_id': account_1_data['id'],
                                  'receiver_account_id': account_2_data['id'],
                                  'amount': 250
                              }),
                              headers={'Content-Type': 'application/json'}
                              ).json()

transaction_history_1_account_1 = requests.get(f'{url}/get-transactions/{account_1_data["id"]}').json()
print("Transaction history account 1 after transfer:", transaction_history_1_account_1)

initial_transaction_history_1_account_2 = requests.get(f'{url}/get-transactions/{account_2_data["id"]}').json()
print("Transaction history account 2 after transfer:", initial_transaction_history_1_account_2)

final_account_1_balance = requests.get(f'{url}/get-account-balance/{account_1_data["id"]}').json()
print("Final account 1 balance:", final_account_1_balance)

final_account_2_balance = requests.get(f'{url}/get-account-balance/{account_2_data["id"]}').json()
print("Final account 2 balance:", final_account_2_balance)


# Send 1000 from account 1 to account 2 - Do this one concurrently
def concurrent_transaction(id: int):
    logging.info(f"Starting transaction {id}")
    transfer = requests.post(f'{url}/create-transaction', json.dumps({
        'sender_account_id': account_2_data['id'],
        'receiver_account_id': account_1_data['id'],
        'amount': 1000
    }),
                             headers={'Content-Type': 'application/json'}
                             ).json()
    logging.info(f"Completed transaction {id}: {transfer}")
    return transfer


# Create threads for concurrent transactions
threads = []
for i in range(2):
    thread = threading.Thread(target=concurrent_transaction, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

for thread in threads:
    logging.info(f"Transaction result: {thread}")

final_transaction_history_account_1 = requests.get(f'{url}/get-transactions/{account_1_data["id"]}').json()
print("Final transaction history account 1:", final_transaction_history_account_1)

final_transaction_history_account_2 = requests.get(f'{url}/get-transactions/{account_2_data["id"]}').json()
print("Final transaction history account 2:", final_transaction_history_account_2)

final_concurrent_account_1_balance = requests.get(f'{url}/get-account-balance/{account_1_data["id"]}').json()
print("Final account 1 balance after concurrent transactions:", final_concurrent_account_1_balance)

final_concurrent_account_2_balance = requests.get(f'{url}/get-account-balance/{account_2_data["id"]}').json()
print("Final account 2 balance after concurrent transactions:", final_concurrent_account_2_balance)
