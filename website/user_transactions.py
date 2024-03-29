from database import transactions_collection

def load_user_transactions(username):
    # Finds user info through username and grabs the information
    user_transactions = transactions_collection.find_one({"username": username})
    if user_transactions:
        return user_transactions.get("transactions", [])
    else:
        return []

def add_user_transaction(username, transaction):
    user_transactions = load_user_transactions(username)
    user_transactions.append(transaction)

    # inserts and updates new transaction
    transactions_collection.update_one(
        {"username": username},
        {"$set": {"transactions": user_transactions}},
        upsert=True
    )
