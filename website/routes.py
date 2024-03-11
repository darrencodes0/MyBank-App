from flask import Blueprint, redirect, render_template, request, session, url_for
from user_info import reset_user_password, load_user_info, save_user_info, save_user_credientials, authenticate_user
from user_transactions import add_transaction, load_user_transactions
from datetime import datetime

auth = Blueprint('auth', __name__)   
date_time = datetime.now()
proper_datetime = date_time.strftime("%H:%M | %Y-%m-%d")

try: # loads user_info if found file
    user_info = load_user_info()
except FileNotFoundError:
    user_info = []

# start of the application
@auth.route("/", methods=["GET"])
def start():
    return render_template("front_page.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            authenticated = authenticate_user(user_info, username, password)

            if authenticated:
                session['username'] = username
                #establish current session's username as current user's username
                return redirect(url_for("auth.accountPage")) 
            else:
                return render_template("login.html",message="Login failed, Please check your user credentials")

    return render_template("login.html")

@auth.route("/resetPassword", methods=["GET", "POST"])
def reset_password():
    message = None
    
    if request.method == "POST":
        username = request.form.get("username")
        secret_word = request.form.get("secret_word")
        new_password = request.form.get("password")  # Get new password from form

        if not username:
            return render_template("forgot_password.html", message="Username is not provided")
        
        if not secret_word:
            return render_template("forgot_password.html", message="Secret word is not provided")

        if new_password:
            # Check if there's a number and special character is in password
            has_number = False
            has_special = False

            for char in new_password:
                if char.isdigit():
                    has_number = True
                elif char in "!@#$%^&*()-_=+":
                    has_special = True

            if not (has_number and has_special):
                return render_template("forgot_password.html", message="Password must contain at least one special character and one number")

            resetted = reset_user_password(user_info, username, secret_word, new_password) 

            if resetted:
                return render_template("forgot_password.html",message="Password successfully changed")
            else:
                return render_template("forgot_password.html",message="Username or/and secret word was incorrect")
                  
        else:
            return render_template("forgot_password.html", message="Password is not provided")

    return render_template("forgot_password.html", message=message)



@auth.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")

        for user_data in user_info:
            if user_data["username"].lower() == new_username.lower():
                return render_template("register.html", message="Username is already taken")

        if new_password:
            # Check if theres a number and special character is in password
            has_number = False
            has_special = False

            for char in new_password:
                if char.isdigit():
                    has_number = True
                elif char in "!@#$%^&*()-_=+":
                    has_special = True

            if not (has_number and has_special):
                return render_template("register.html", message="Password must contain at least one special character and one number")

            save_user_credientials(user_info, new_username, new_password)
            return redirect(url_for("auth.login"))
        else:
            return render_template("register.html", message="Password is not provided")

    return render_template("register.html")


@auth.route("/accountpage", methods=["GET"])
def accountPage():
    username = session.get('username')
    for user_data in user_info:
        if user_data["username"] == username:
            #establishes info of the logged-in user to be of the current session
            loan = user_data["loan"]
            session['loan'] = loan
            secret_word = user_data["secret_word"]
            session['secret_word'] = secret_word
            current_balance = user_data["balance"]
            session['balance'] = current_balance
            break

    return render_template("account_page.html", user=username, current_balance=current_balance, loan=loan, secret_word=secret_word)

@auth.route("/logout")
def logout():
    #removes all information fromso s session dictionary so next user doesn't inherit previous user's information
    try:
        session.pop('username')
    except KeyError:
        pass
    
    try:
        session.pop('balance')
    except KeyError:
        pass

    try:
        session.pop('secret_word')
    except KeyError:
        pass

    try:
        session.pop('loan')
    except KeyError:
        pass

    return redirect(url_for('auth.start'))


@auth.route("/deposit", methods=["GET", "POST"])
def deposit():
    current_balance = session.get('balance')
    if request.method == "POST":
        amount = request.form.get("amount")

        try:
            amount = float(amount)
        except ValueError:
            return render_template("deposit.html", current_balance=current_balance, message="Incorrect Input")
        
        if amount <= 0:
            return render_template("deposit.html", current_balance=current_balance, message="Invalid Amount")
        
        for user_data in user_info:
            if user_data["username"] == session['username']:
                user_data["balance"] = round(user_data["balance"] + float(amount), 2)
                current_balance = user_data["balance"]
                session['balance'] = current_balance
                save_user_info(user_info) 
                add_transaction(session['username'], f"({proper_datetime}) - Deposited ${amount} into your bank account")
                return render_template("deposit.html", current_balance=current_balance, message=f"Deposited ${amount} into your bank account")
        
        return render_template("deposit.html", current_balance=current_balance, message="User not found")
    
    return render_template("deposit.html", current_balance=current_balance)


@auth.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    current_balance = session.get('balance')
    if request.method == "POST":
        amount = request.form.get("amount")
        
        try:
            amount = float(amount)
        except ValueError:
            return render_template("withdrawal.html", current_balance=current_balance, message="Incorrect Input")
        
        if amount <= 0:
            return render_template("withdrawal.html", current_balance=current_balance, message="Invalid Amount")
        
        amount = round(amount, 2)
        
        if amount > current_balance:
            return render_template("withdrawal.html", current_balance=current_balance, message="Insufficient Balance")
        
        for user_data in user_info:
            if user_data["username"] == session['username']:
                user_data["balance"] = round(user_data["balance"] - amount, 2)
                current_balance = user_data["balance"]
                session['balance'] = current_balance
                save_user_info(user_info) 
                add_transaction(session['username'], f"({proper_datetime}) - Withdrawn ${amount} from your bank account")
                return render_template("withdrawal.html", current_balance=current_balance, message=f"Withdrawn ${amount} from your bank account")
        
        return render_template("withdrawal.html", current_balance=current_balance, message="User not found")
    
    return render_template("withdrawal.html", current_balance=current_balance)


@auth.route("/transactions")
def transactions():
    username = session.get('username')
    user_transactions = load_user_transactions(username)
    return render_template("transactions.html", transactions=user_transactions)

@auth.route("/loans")
def loans():
    return render_template("loans.html")

@auth.route("/pay_loan", methods=["GET", "POST"])
def pay_loan():
    current_balance = session.get('balance')
    loan = session.get('loan')
    if request.method == "POST":
        amount = request.form.get("amount")

        try:
            amount = float(amount)
        except ValueError:
            return render_template("pay_loan.html", current_balance=current_balance, message="Incorrect Input", loan=loan)

        if amount <= 0:
            return render_template("pay_loan.html", current_balance=current_balance, message="Invalid Amount", loan=loan)

        amount = round(amount, 2)

        for user_data in user_info:
            if user_data["username"] == session['username']:
                if amount == loan and amount <= user_data["balance"]:
                    user_data["balance"] = round(user_data["balance"] - amount, 2)
                    user_data["loan"] = 0
                    current_balance = user_data["balance"]
                    session['balance'] = current_balance
                    session['loan'] = 0
                    save_user_info(user_info)
                    add_transaction(session['username'], f"({proper_datetime}) - Paid ${amount} loans off")
                    return render_template("pay_loan.html", current_balance=current_balance, message=f"Paid ${amount} loans off", loan=0)
                elif amount <= user_data["balance"] and amount <= loan:
                    user_data["balance"] = round(user_data["balance"] - amount, 2)
                    user_data["loan"] = round(user_data["loan"] - amount, 2)
                    current_balance = user_data["balance"]
                    loan = user_data["loan"]
                    session['loan'] = loan
                    session['balance'] = current_balance
                    save_user_info(user_info)  

                    add_transaction(session['username'], f"({proper_datetime}) - Paid ${amount} loans off")
                    return render_template("pay_loan.html", current_balance=current_balance, message=f"Paid ${amount} loans off", loan=loan)
                else:
                    return render_template("pay_loan.html", current_balance=current_balance, message="Cannot pay more than loan amount or insufficient funds", loan=loan)
        return render_template("pay_loan.html", current_balance=current_balance, message="User not found", loan=loan)
    return render_template("pay_loan.html", current_balance=current_balance, loan=loan)


@auth.route("/request_loan", methods=["GET", "POST"])
def request_loan():
    current_balance = session.get('balance')
    loan = session.get('loan')

    if request.method == "POST":
        amount = request.form.get("amount")

        try:
            amount = float(amount)
        except ValueError:
            return render_template("request_loan.html", current_balance=current_balance, message="Incorrect Input", loan=loan)

        if amount <= 0:
            return render_template("request_loan.html", current_balance=current_balance, message="Invalid Amount", loan=loan)

        amount = round(amount, 2)

        for user_data in user_info:
            if user_data["username"] == session['username']:
                user_data["balance"] = round(user_data["balance"] + amount, 2)
                user_data["loan"] = round(user_data["loan"] + (amount * 1.25), 2)  # 25% set interest rate to loan added
                current_balance = user_data["balance"]
                loan = user_data["loan"]
                session['balance'] = current_balance
                session['loan'] = loan
                save_user_info(user_info)  
                add_transaction(session['username'], f"({proper_datetime}) - Added ${amount} in loans to your bank account")
                return render_template("request_loan.html", current_balance=current_balance, message=f"Added ${amount} in loans to your bank account", loan=loan)
        return render_template("request_loan.html", current_balance=current_balance, message="User not found", loan=loan)
    return render_template("request_loan.html", current_balance=current_balance, loan=loan)

@auth.route("/transfer", methods=["GET", "POST"])
def transfer():
    current_balance = session.get('balance')
    if request.method == "POST":
        amount = request.form.get("amount")
        recipient_username = request.form.get("username")

        try:
            amount = float(amount)
        except ValueError:
            return render_template("transfer.html", current_balance=current_balance, message="Incorrect Input")

        if amount <= 0:
            return render_template("transfer.html", current_balance=current_balance, message="Invalid Amount")

        amount = round(amount, 2)

        if amount > current_balance:
            return render_template("transfer.html", current_balance=current_balance, message="Insufficient Balance")

        for user_data in user_info:
            if user_data["username"] == session['username']:
                    for recipient_data in user_info:
                        if recipient_data["username"] == recipient_username and recipient_username != session['username']:
                            user_data["balance"] = round(user_data["balance"] - amount, 2)
                            current_balance = user_data["balance"]
                            session['balance'] = current_balance
                            recipient_data["balance"] = round(recipient_data["balance"] + amount, 2)
                            save_user_info(user_info)
                            add_transaction(session['username'], f"({proper_datetime}) - Transferred ${amount} to {recipient_username}")
                            add_transaction(recipient_data['username'], f"({proper_datetime}) - Recieved ${amount} from {session['username']}")
                            return render_template("transfer.html", current_balance=session['balance'], message=f"Transferred ${amount} to {recipient_username}")
                    return render_template("transfer.html", current_balance=current_balance, message="Recipient not found or can't transfer to self")
        return render_template("transfer.html", current_balance=current_balance, message="User not found")

    return render_template("transfer.html", current_balance=current_balance)

@auth.route("/about")
def about():
    return render_template("about.html")