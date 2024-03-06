import json
from passlib.context import CryptContext

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def load_user_info():
    try: # reads json file and loads it
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

# checks if username and password matches with user in database
def authenticate_user(user_info, username, password):
    for user_data in user_info:
        if username.lower() == user_data["username"].lower() and verify_password(password, user_data["password"]):
            return True
    return False

#registering will encrypt your password and store it into user_info
def save_user_credientials(user_info, new_username, new_password):
    user_info.append({"username": new_username, "password": encrypt_password(new_password), "balance": 0, "loan": 0})
    with open("user_info.json", "w") as file:
        json.dump(user_info, file)