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
    try:
        with open("user_info.json", "w") as file:
            json.dump(user_info, file)
    except Exception as e:
        print(f"Error: saving user's info = {e}")

#encrypts password
def encrypt_password(password):
    try:
        return crypt_context.hash(password)
    except Exception as e: 
        print(f"Error: Couldn't encrypt password - {e}")

def verify_password(password, hashed_password):
    try:
        return crypt_context.verify(password, hashed_password)
    except Exception as e: 
        print(f"Error: Couldn't verify password - {e}")

# checks if username and password matches in user_info
def authenticate_user(user_info, username, password):
    try:
        for user_data in user_info:
            if username.lower() == user_data["username"].lower() and verify_password(password, user_data["password"]):
                return True
        return False
    except Exception as e: 
        print(f"Error: Authenticating user - {e}")

#secret word is used for resetting password, generates random for each unique user
def generate_secret_word():
    try:
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
    except Exception as e: 
        print(f"Error: Generating secret word for user - {e}")    

#registering will encrypt your password and store it into user_info
def save_user_credientials(user_info, new_username, new_password):
    try:
        secret_word = generate_secret_word()
        user_info.append({
            "username": new_username, 
            "password": encrypt_password(new_password), 
            "balance": 0, 
            "loan": 0, 
            "secret_word": secret_word
        })
        save_user_info(user_info)
    except Exception as e: 
        print(f"Error: Saving user credentials - {e}")

#changes password of user when resetting, requires secret word
def reset_user_password(user_info, username, secret_word, new_password):
    try:
        for user_data in user_info:
                if user_data["username"].lower() == username.lower() and user_data["secret_word"].lower() == secret_word.lower():
                    user_data["password"] = encrypt_password(new_password)
                    return True
        return False
    except Exception as e: 
        print(f"Error: Resetting user password - {e}")
