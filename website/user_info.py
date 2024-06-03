import random
from passlib.context import CryptContext
from database import user_collection

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def load_user_info():
    return list(user_collection.find())

def save_user_info(user_info):
    user_collection.delete_many({})
    user_collection.insert_many(user_info)

def encrypt_password(password):
    return crypt_context.hash(password)

def verify_password(password, hashed_password):
    return crypt_context.verify(password, hashed_password)

def authenticate_user(username, password):
    user_data = user_collection.find_one({"username": username.lower()})
    if user_data and verify_password(password, user_data["password"]):
        return True
    return False

def generate_secret_word():
    words = [
        "apple",
        "pear",
        "hidden",
        "banana",
        "orange",
        "grape",
        "pineapple",
        "kiwi",
        "strawberry",
        "blueberry",
        "watermelon",
        "mango",
        "dragonfruit"
    ]
    random_word = random.choice(words)
    random_number = random.randint(1000, 9999)
    secret_word = random_word + str(random_number)
    return secret_word

def save_user_credentials(new_username, new_password):
    secret_word = generate_secret_word()
    user_collection.insert_one({
        "username": new_username.lower(),
        "password": encrypt_password(new_password),
        "checking_balance": 0,
        "savings_balance": 0,
        "loan": 0,
        "secret_word": secret_word
    })

def reset_user_password(username, secret_word, new_password):
    user_data = user_collection.find_one({"username": username.lower(), "secret_word": secret_word.lower()})
    if user_data:
        user_collection.update_one({"_id": user_data["_id"]}, {"$set": {"password": encrypt_password(new_password)}})
        return True
    return False

def get_user_balance(username, account_type):
    user_data = user_collection.find_one({"username": username.lower()})
    if user_data:
        return user_data.get(account_type + "_balance", 0)
    else:
        return 0
    
def update_user_balance(username, account_type, new_balance):
    user_collection.update_one(
        {"username": username.lower()},
        {"$set": {account_type + "_balance": new_balance}}
    )

def get_user_loan(username):
    user_data = user_collection.find_one({"username": username.lower()})
    if user_data:
        return user_data.get("loan", 0)
    else:
        return 0
    
def update_user_loan(username, new_loan):
    user_collection.update_one({"username": username.lower()}, {"$set": {"loan": new_loan}})

def get_user_info(username):
    return user_collection.find_one({"username": username.lower()})