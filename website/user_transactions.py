import json
import os

#Folder storing transactions of each user
TRANSACTIONS_FOLDER = "transactions_data"

#looks for user folder in transaction folder and loads it
def load_user_transactions(username):
    try:
        with open(os.path.join(TRANSACTIONS_FOLDER, f"{username}_transactions.json"), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

#finds transaction folder then creates one with user's name
def save_user_transactions(username, transactions):
    try:
        os.makedirs(TRANSACTIONS_FOLDER, exist_ok=True)
        with open(os.path.join(TRANSACTIONS_FOLDER, f"{username}_transactions.json"), "w") as file:
            json.dump(transactions, file)
    except Exception as e:
        print(f"Error: Saving transaction - {e}")

#adds transaction to specific user
def add_transaction(username, transaction_message):
    try:
        transactions = load_user_transactions(username)
        transactions.append(transaction_message)
        save_user_transactions(username, transactions)
    except Exception as e:
        print(f"Error: Adding transaction - {e}")