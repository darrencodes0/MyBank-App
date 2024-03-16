from flask import Blueprint, redirect, render_template, request, session, url_for
from user_info import reset_user_password, load_user_info, save_user_info, save_user_credientials, authenticate_user
from user_transactions import add_transaction, load_user_transactions
from datetime import datetime

auth = Blueprint('auth', __name__)   
date_time = datetime.now()
proper_datetime = date_time.strftime("%H:%M | %Y-%m-%d")

# loads user_info if found file
try: 
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
    if request.method == "POST":
        username = request.form.get("username")
        secret_word = request.form.get("secret_word")
        new_password = request.form.get("password")  # Gets new password to override current password

        if not username:
            return render_template("forgot_password.html", message="Username is not provided")
        
        if not secret_word:
            return render_template("forgot_password.html", message="Secret word is not provided")

        if new_password:
            # Checks if theres a number and special character is in password
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

    return render_template("forgot_password.html", message="ERROR: UNEXPECTED")



@auth.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")

        for user_data in user_info:
            if user_data["username"] == new_username.lower():
                return render_template("register.html", message="Username is already taken")

        if new_password:
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
            loan = "{:,}".format(user_data["loan"]) # formats by 3 digits (ex. 1,000 , 1,000,000)
            session['loan'] = user_data["loan"]
            secret_word = user_data["secret_word"]
            session['secret_word'] = secret_word
            checking_balance = "{:,}".format(user_data["checking_balance"])
            session['checking_balance'] = user_data["checking_balance"]
            savings_balance = "{:,}".format(user_data["savings_balance"])
            session['savings_balance'] = user_data["savings_balance"]
            break

    return render_template("account_page.html", user=username, checking_balance=checking_balance, savings_balance=savings_balance, loan=loan, secret_word=secret_word)

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.start'))

@auth.route("/deposit", methods=["GET", "POST"])
def deposit():
    checking_balance = session.get('checking_balance')
    savings_balance = session.get('savings_balance')

    if request.method == "POST":
        amount = request.form.get("amount")
        account_type = request.form.get("account_type")  # Get the selected account type

        try:
            amount = float(amount)
        except ValueError:
            return render_template("deposit.html", checking_balance=checking_balance, savings_balance=savings_balance, message="Incorrect Input")
        
        if amount <= 0:
            return render_template("deposit.html", checking_balance=checking_balance, savings_balance=savings_balance, message="Invalid Amount")
        
        for user_data in user_info:
            if user_data["username"] == session['username']:
                if account_type == "checking":  # Deposits into checking account
                    user_data["checking_balance"] = round(user_data["checking_balance"] + float(amount), 2)
                    checking_balance = user_data["checking_balance"]
                    session['checking_balance'] = checking_balance
                elif account_type == "savings":  # Deposits into savings account
                    user_data["savings_balance"] = round(user_data["savings_balance"] + float(amount), 2)
                    savings_balance = user_data["savings_balance"]
                    session['savings_balance'] = savings_balance
                
                save_user_info(user_info) 
                add_transaction(session['username'], f"({proper_datetime}) - Deposited ${amount} into your {account_type} account")
                return render_template("deposit.html",  checking_balance=checking_balance, savings_balance=savings_balance, message=f"Deposited ${amount} into your {account_type} account")
        
        return render_template("deposit.html",  checking_balance=checking_balance, savings_balance=savings_balance, message="User not found")
    
    return render_template("deposit.html",  checking_balance=checking_balance, savings_balance=savings_balance,)



@auth.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    checking_balance = session.get("checking_balance")
    savings_balance = session.get("savings_balance")

    if request.method == "POST":
        amount = request.form.get("amount")
        account_type = request.form.get("account_type")
    
        try:
            amount = float(amount)
        except ValueError:
            return render_template("withdrawal.html", checking_balance=checking_balance, savings_balance=savings_balance, message="Incorrect Input")
        
        if amount <= 0:
            return render_template("withdrawal.html", checking_balance=checking_balance, savings_balance=savings_balance, message="Invalid Amount")
        
        amount = round(amount, 2)
        
        for user_data in user_info:
            if user_data["username"] == session['username']:
                if account_type == "checking":  # Withdraw from checking account
                    if amount > user_data["checking_balance"]:
                        return render_template("withdrawal.html", checking_balance=checking_balance, savings_balance=savings_balance, message="Insufficient Balance in checking account")
                    user_data["checking_balance"] = round(user_data["checking_balance"] - amount, 2)
                    checking_balance = user_data["checking_balance"]
                    session['checking_balance'] = checking_balance
                elif account_type == "savings":  # Withdraw from savings account
                    if amount > user_data["savings_balance"]:
                        return render_template("withdrawal.html", checking_balance=checking_balance, savings_balance=savings_balance, message="Insufficient Balance in savings account")
                    user_data["savings_balance"] = round(user_data["savings_balance"] - amount, 2)
                    savings_balance = user_data["savings_balance"]
                    session['savings_balance'] = savings_balance

                save_user_info(user_info) 
                add_transaction(session['username'], f"({proper_datetime}) - Withdrawn ${amount} from your {account_type} account")
                return render_template("withdrawal.html", checking_balance=checking_balance, savings_balance=savings_balance, message=f"Withdrawn ${amount} from your {account_type} account")
        
        return render_template("withdrawal.html",  checking_balance=checking_balance, savings_balance=savings_balance, message="User not found")
    
    return render_template("withdrawal.html",  checking_balance=checking_balance, savings_balance=savings_balance)


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
    checking_balance = session.get('checking_balance')
    loan = session.get('loan')

    if request.method == "POST":
        amount = request.form.get("amount")
        account_type = "checking"

        try:
            amount = float(amount)
        except ValueError:
            return render_template("pay_loan.html",  checking_balance=checking_balance, message="Incorrect Input", loan=loan)

        if amount <= 0:
            return render_template("pay_loan.html",  checking_balance=checking_balance, message="Invalid Amount", loan=loan)

        amount = round(amount, 2)

        for user_data in user_info:
            if user_data["username"] == session['username']:
                if amount == loan and amount <= user_data["checking_balance"]:
                    user_data["checking_balance"] = round(user_data["checking_balance"] - amount, 2)
                    user_data["loan"] = 0
                    current_balance = user_data["checking_balance"]
                    session["checking_balance"] = current_balance
                    session['loan'] = 0
                    save_user_info(user_info)
                    add_transaction(session['username'], f"({proper_datetime}) - Paid ${amount} loans off from checking account")
                    return render_template("pay_loan.html", checking_balance=checking_balance, message=f"Paid ${amount} loans off from checking account", loan=0)
                elif amount <= user_data["checking_balance"] and amount <= loan:
                    user_data["checking_balance"] = round(user_data["checking_balance"] - amount, 2)
                    user_data["loan"] = round(user_data["loan"] - amount, 2)
                    current_balance = user_data["checking_balance"]
                    loan = user_data["loan"]
                    session['loan'] = loan
                    session[f"{account_type}_balance"] = current_balance
                    save_user_info(user_info)  
                    add_transaction(session['username'], f"({proper_datetime}) - Paid ${amount} loans off")
                    return render_template("pay_loan.html", checking_balance=checking_balance, message=f"Paid ${amount} loans off from checking account", loan=loan)
                else:
                    return render_template("pay_loan.html", checking_balance=checking_balance, message="Cannot pay more than loan amount or insufficient funds", loan=loan)
        return render_template("pay_loan.html", checking_balance=checking_balance, message="User not found", loan=loan)
    return render_template("pay_loan.html", checking_balance=checking_balance, loan=loan)

@auth.route("/request_loan", methods=["GET", "POST"])
def request_loan():
    checking_balance = session.get('checking_balance')
    loan = session.get('loan')

    if request.method == "POST":
        amount = request.form.get("amount")
        try:
            amount = float(amount)
        except ValueError:
            return render_template("request_loan.html", checking_balance=checking_balance, message="Incorrect Input", loan=loan)

        if amount <= 0:
            return render_template("request_loan.html", checking_balance=checking_balance, message="Invalid Amount", loan=loan)

        amount = round(amount, 2)

        for user_data in user_info:
            if user_data["username"] == session['username']:                
                if amount <= checking_balance:  # Ensures sufficient funds in user's account before allowing loan request
                    user_data["checking_balance"] = round(checking_balance + amount, 2)
                    loan_given = round(amount * 1.18)
                    user_data["loan"] = round(user_data["loan"] + loan_given, 2)  # 18% fixed interest rate added to loan
                    session['checking_balance'] = user_data["checking_balance"]  
                    session['loan'] = user_data["loan"]
                    save_user_info(user_info)  
                    add_transaction(session['username'], f"({proper_datetime}) - Added ${amount} in loans to your checkings account")
                    return render_template("request_loan.html", checking_balance=checking_balance, message=f"Added ${amount} to your checkings account",loan_given=f"Additional loan amount added: ${loan_given}", loan=loan)
                else:
                    return render_template("request_loan.html", checking_balance=checking_balance, message=f"You may only request a loan if you have either more or equal to the funds you request in your checkings account", loan=loan)

        return render_template("request_loan.html",  checking_balance=checking_balance, message="User not found", loan=loan)
    return render_template("request_loan.html",  checking_balance=checking_balance, loan=loan)


@auth.route("/sendfunds", methods=["GET", "POST"])
def send_money():
    checking_balance = session.get('checking_balance')
    if request.method == "POST":
        amount = request.form.get("amount")
        recipient_username = request.form.get("username")

        try:
            amount = float(amount)
        except ValueError:
            return render_template("send_money.html", checking_balance=checking_balance, message="Incorrect Input")

        if amount <= 0:
            return render_template("send_money.html", checking_balance=checking_balance, message="Invalid Amount")

        amount = round(amount, 2)

        if amount > checking_balance:
            return render_template("send_money.html", checking_balance=checking_balance, message="Insufficient Balance")

        for user_data in user_info:
            if user_data["username"] == session['username']:
                for recipient_data in user_info:
                    if recipient_data["username"] == recipient_username and recipient_username != session['username']:
                        user_data["checking_balance"] = round(user_data["checking_balance"] - amount, 2)
                        checking_balance = user_data["checking_balance"]
                        session["checking_balance"] = checking_balance
                        recipient_data["checking_balance"] = round(recipient_data["checking_balance"] + amount, 2)
                        save_user_info(user_info)
                        add_transaction(session['username'], f"({proper_datetime}) - Transferred ${amount} to {recipient_username}")
                        add_transaction(recipient_data['username'], f"({proper_datetime}) - Received ${amount} from {session['username']}")
                        return render_template("send_money.html", checking_balance=checking_balance, message=f"Transferred ${amount} to {recipient_username} from checking account")
                    return render_template("send_money.html", checking_balance=checking_balance, message="Recipient not found or can't transfer to self")
        return render_template("send_money.html", checking_balance=checking_balance, message="User not found")

    return render_template("send_money.html", checking_balance=checking_balance)

@auth.route("/transfer", methods=["GET", "POST"])
def transfer():
    checking_balance = session.get("checking_balance")
    savings_balance = session.get("savings_balance")

    if request.method == "POST":
        amount = request.form.get("amount")
        account_type = request.form.get("account_type")
    
        try:
            amount = float(amount)
        except ValueError:
            return render_template("transfer.html", checking_balance=checking_balance, savings_balance=savings_balance, message="Incorrect Input")
        
        if amount <= 0:
            return render_template("transfer.html", checking_balance=checking_balance, savings_balance=savings_balance, message="Invalid Amount")
        
        amount = round(amount, 2)
        
        for user_data in user_info:
            if user_data["username"] == session['username']:
                if amount > user_data[f"{account_type}_balance"]:
                        return render_template("withdrawal.html", checking_balance=checking_balance, savings_balance=savings_balance, message=f"Insufficient Balance in {account_type} account")
                if account_type == "checking":  # Withdraw from checking account
                    user_data["checking_balance"] = round(user_data["checking_balance"] - amount, 2)
                    session['checking_balance'] = user_data["checking_balance"]
                    #adds to savings from checking
                    user_data["savings_balance"] = round(user_data["savings_balance"] + float(amount), 2)
                    session['savings_balance'] = user_data["savings_balance"]
                    savings_balance = session['savings_balance']
                    checking_balance = session['checking_balance']
                elif account_type == "savings":  # Withdraw from savings account
                    user_data["savings_balance"] = round(user_data["savings_balance"] - amount, 2)
                    session['savings_balance'] = user_data["savings_balance"]
                    #adds to checking from savings
                    user_data["checking_balance"] = round(user_data["checking_balance"] + float(amount), 2)
                    session['checking_balance'] = user_data["checking_balance"]
                    savings_balance = session['savings_balance']
                    checking_balance = session['checking_balance']

                save_user_info(user_info) 
                add_transaction(session['username'], f"({proper_datetime}) - Transferred ${amount} from your {account_type} account to your other account")
                return render_template("transfer.html", checking_balance=checking_balance, savings_balance=savings_balance, message=f"Transferred ${amount} from your {account_type} account to your other account")
        
        return render_template("transfer.html",  checking_balance=checking_balance, savings_balance=savings_balance, message="User not found")
    
    return render_template("transfer.html",  checking_balance=checking_balance, savings_balance=savings_balance)


@auth.route("/about")
def about():
    return render_template("about.html")