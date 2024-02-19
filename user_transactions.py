import json
import os

TRANSACTIONS_FOLDER = "transactions_data"

def load_user_transactions(username):
    try:
        with open(os.path.join(TRANSACTIONS_FOLDER, f"{username}_transactions.json"), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_user_transactions(username, transactions):
    os.makedirs(TRANSACTIONS_FOLDER, exist_ok=True)
    with open(os.path.join(TRANSACTIONS_FOLDER, f"{username}_transactions.json"), "w") as file:
        json.dump(transactions, file)

def add_transaction(username, transaction_message):
    transactions = load_user_transactions(username)
    transactions.append(transaction_message)
    save_user_transactions(username, transactions)
