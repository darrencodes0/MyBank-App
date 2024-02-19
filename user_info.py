import json

def load_user_info():
    try:
        with open("user_info.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_user_info(user_info):
    with open("user_info.json", "w") as file:
        json.dump(user_info, file)

def authenticate_user(user_info, username, password):
    for user_data in user_info:
        if username.lower() == user_data["username"].lower() and password == user_data["password"]:
            return True
    return False