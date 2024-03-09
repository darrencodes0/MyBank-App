import json
import random
from passlib.context import CryptContext

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# reads json file and loads it
def load_user_info():
    try: 
        with open("user_info.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    
# writes new info into json file to "save"
def save_user_info(user_info):
    with open("user_info.json", "w") as file:
        json.dump(user_info, file)

#encrypts password
def encrypt_password(password):
    return crypt_context.hash(password)

def verify_password(password, hashed_password):
    return crypt_context.verify(password, hashed_password)

# checks if username and password matches in user_info
def authenticate_user(user_info, username, password):
    for user_data in user_info:
        if username.lower() == user_data["username"].lower() and verify_password(password, user_data["password"]):
            return True
    return False

#secret word is used for resetting password, generates random for each unique user
def generate_secret_word():
    words = [
            "car",
            "apple",
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
    random_number = random.randint(1000,9999)  # Adjust range as needed
    secret_word = random_word + str(random_number)
    return secret_word

#registering will encrypt your password and store it into user_info
def save_user_credientials(user_info, new_username, new_password):
    secret_word = generate_secret_word()
    user_info.append({
        "username": new_username, 
        "password": encrypt_password(new_password), 
        "balance": 0, 
        "loan": 0, 
        "secret_word": secret_word
    })
    with open("user_info.json", "w") as file:
        json.dump(user_info, file)

#changes password of user when resetting, requires secret word
def reset_user_password(user_info, username, secret_word, new_password):
    for user_data in user_info:
            if user_data["username"].lower() == username.lower() and user_data["secret_word"].lower() == secret_word.lower():
                user_data["password"] = encrypt_password(new_password)
                return True
    return False
