from flask import Blueprint, redirect, render_template, request, session, url_for
from user_info import reset_user_password, save_user_credentials, authenticate_user, get_user_balance, update_user_balance, get_user_loan, update_user_loan, get_user_info
from user_transactions import load_user_transactions, add_user_transaction
from database import user_collection
from datetime import datetime

auth = Blueprint('auth', __name__)   
date_time = datetime.now()
proper_datetime = date_time.strftime("%H:%M | %Y-%m-%d")

def validate_password(password):
    has_number = any(char.isdigit() for char in password)
    has_special = any(char in "!@#$%^&*()-_=+" for char in password)
    return has_number and has_special

@auth.route("/", methods=["GET"])
def start():
    return render_template("front_page.html")

@auth.route("/about")
def about():
    return render_template("about.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.start'))

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        username_lower = username.lower()

        if authenticate_user(username_lower, password):
            session['username'] = username
            return redirect(url_for("auth.accountPage"))
        else:
            return render_template("login.html", message="Login failed, Please check your user credentials")

    return render_template("login.html")

@auth.route("/resetPassword", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        username = request.form.get("username")
        secret_word = request.form.get("secret_word")
        new_password = request.form.get("password")

        if not username:
            return render_template("forgot_password.html", message="Username is not provided")

        if not secret_word:
            return render_template("forgot_password.html", message="Secret word is not provided")

        if new_password:
            if not validate_password(new_password):
                return render_template("register.html", message="Password must contain at least one special character and one number")

            resetted = reset_user_password(username, secret_word, new_password)

            if resetted:
                return render_template("forgot_password.html", message="Password successfully changed")
            else:
                return render_template("forgot_password.html", message="Username or/and secret word was incorrect")
        else:
            return render_template("forgot_password.html", message="Password is not provided")

    return render_template("forgot_password.html", message="ERROR: UNEXPECTED")

@auth.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        
        if user_collection.find_one({"username": new_username.lower()}):
            return render_template("register.html", message="Username is already taken")
        
        if new_password:
            if not validate_password(new_password):
                return render_template("register.html", message="Password must contain at least one special character and one number")

        save_user_credentials(new_username, new_password)
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth.route("/accountpage", methods=["GET"])
def accountPage():
    username = session.get('username')
    user_data = user_collection.find_one({"username": username})

    if user_data:
        # Retrieves user information within database and sets it in current session
        loan = "{:,}".format(user_data["loan"])
        session['loan'] = user_data["loan"]
        secret_word = user_data["secret_word"]
        session['secret_word'] = secret_word
        checking_balance = "{:,}".format(user_data["checking_balance"])
        session['checking_balance'] = user_data["checking_balance"]
        savings_balance = "{:,}".format(user_data["savings_balance"])
        session['savings_balance'] = user_data["savings_balance"]
        
        return render_template("account_page.html", user=username, checking_balance=checking_balance, savings_balance=savings_balance, loan=loan, secret_word=secret_word)
    else:
        return render_template("account_page.html", message="User not found")

@auth.route("/deposit", methods=["GET", "POST"])
def deposit():
    if request.method == "POST":
        amount = request.form.get("amount")
        account_type = request.form.get("account_type")
        username = session.get('username')

        try:
            amount = float(amount)
        except ValueError:
            return render_template("deposit.html", message="Incorrect Input")

        if amount <= 0:
            return render_template("deposit.html", message="Invalid Amount")

        checking_balance = get_user_balance(username, "checking")
        savings_balance = get_user_balance(username, "savings")

        if account_type == "checking":
            new_balance = checking_balance + amount
        elif account_type == "savings":
            new_balance = savings_balance + amount

        update_user_balance(username, account_type, new_balance)
        add_user_transaction(username, f"({proper_datetime}) - Deposited ${amount} into your {account_type} account")

        checking_balance = get_user_balance(username, "checking")
        savings_balance = get_user_balance(username, "savings")

        return render_template("deposit.html", checking_balance=checking_balance, savings_balance=savings_balance, message=f"Deposited ${amount} into your {account_type} account")
    
    return render_template("deposit.html", checking_balance=session.get("checking_balance"), savings_balance=session.get("savings_balance"))

@auth.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if request.method == "POST":
        amount = request.form.get("amount")
        account_type = request.form.get("account_type")
        username = session.get('username')

        try:
            amount = float(amount)
        except ValueError:
            return render_template("withdrawal.html", message="Incorrect Input")

        if amount <= 0:
            return render_template("withdrawal.html", message="Invalid Amount")

        checking_balance = get_user_balance(username, "checking")
        savings_balance = get_user_balance(username, "savings")

        if account_type == "checking" and amount > checking_balance:
            return render_template("withdrawal.html", message="Insufficient Balance")
        elif account_type == "savings" and amount > savings_balance:
            return render_template("withdrawal.html", message="Insufficient Balance")

        if account_type == "checking":
            new_balance = checking_balance - amount
        elif account_type == "savings":
            new_balance = savings_balance - amount

        update_user_balance(username, account_type, new_balance)
        add_user_transaction(username, f"({proper_datetime}) - Withdrawn ${amount} from your {account_type} account")

        checking_balance = get_user_balance(username, "checking")
        savings_balance = get_user_balance(username, "savings")

        return render_template("withdrawal.html", checking_balance=checking_balance, savings_balance=savings_balance, message=f"Withdrawn ${amount} from your {account_type} account")

    return render_template("withdrawal.html", checking_balance=session.get("checking_balance"), savings_balance=session.get("savings_balance"))

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
    username = session.get('username')
    loan = get_user_loan(username)  
    checking_balance = get_user_balance(username, "checking") 

    if request.method == "POST":
        amount = request.form.get("amount")

        try:
            amount = float(amount)
        except ValueError:
            return render_template("pay_loan.html", loan=loan, checking_balance=checking_balance, message="Incorrect Input")

        if amount <= 0:
            return render_template("pay_loan.html", loan=loan, checking_balance=checking_balance, message="Invalid Amount")

        if amount > loan:
            return render_template("pay_loan.html", loan=loan, checking_balance=checking_balance, message="Cannot pay more than loan amount")
        
        current_checking_balance = get_user_balance(username, "checking")
        new_balance = current_checking_balance - amount
        update_user_balance(username, "checking", new_balance)

        new_loan = loan - amount
        update_user_loan(username, new_loan)

        add_user_transaction(username, f"({proper_datetime}) - Paid ${amount} of your loan")

        return render_template("pay_loan.html", loan=loan, checking_balance=new_balance, message=f"Paid ${amount} of your loan")

    return render_template("pay_loan.html", loan=loan, checking_balance=checking_balance)

@auth.route("/request_loan", methods=["GET", "POST"])
def request_loan():
    username = session.get('username')
    loan = get_user_loan(username)  
    checking_balance = get_user_balance(username, "checking")  

    if request.method == "POST":
        amount = request.form.get("amount")

        try:
            amount = float(amount)
        except ValueError:
            return render_template("request_loan.html", loan=loan, checking_balance=checking_balance, message="Incorrect Input")

        if amount <= 0:
            return render_template("request_loan.html", loan=loan, checking_balance=checking_balance, message="Invalid Amount")

        # Add a fixed 18% interest to the loan amount
        loan_given = round(amount * 1.18)

        current_checking_balance = get_user_balance(username, "checking")
        new_balance = current_checking_balance + amount
        update_user_balance(username, "checking", new_balance)

        new_loan = loan + loan_given
        update_user_loan(username, new_loan)

        add_user_transaction(username, f"({proper_datetime}) - Requested a loan of ${amount} (Total: ${loan_given})")

        return render_template("request_loan.html", loan=new_loan, checking_balance=new_balance, message=f"Requested a loan of ${amount} (Total: ${loan_given})")

    return render_template("request_loan.html", loan=loan, checking_balance=checking_balance)

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

        # Fetches sender and receipt info from database
        sender_username = session['username']
        sender_info = get_user_info(sender_username)
        recipient_info = get_user_info(recipient_username)

        if sender_info and recipient_info:
            if sender_username == recipient_username:
                return render_template("send_money.html", checking_balance=checking_balance, message="Cannot send money to yourself")

            # Updates both sender and recipient's balance
            sender_new_balance = sender_info['checking_balance'] - amount
            recipient_new_balance = recipient_info['checking_balance'] + amount

            update_user_balance(sender_username, "checking", sender_new_balance)
            update_user_balance(recipient_username, "checking", recipient_new_balance)

            add_user_transaction(sender_username, f"({proper_datetime}) - Transferred ${amount} to {recipient_username}")
            add_user_transaction(recipient_username, f"({proper_datetime}) - Received ${amount} from {sender_username}")

            return render_template("send_money.html", checking_balance=sender_new_balance, message=f"Transferred ${amount} to {recipient_username} from checking account")

        return render_template("send_money.html", checking_balance=checking_balance, message="Sender or recipient not found")

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

        if amount > session[f"{account_type}_balance"]:
            return render_template("transfer.html", checking_balance=checking_balance, savings_balance=savings_balance, message=f"Insufficient Balance in {account_type} account")
        
        if account_type == "checking":
            new_checking_balance = checking_balance - amount
            new_savings_balance = savings_balance + amount
            add_user_transaction(username, f"({proper_datetime}) - Transferred ${amount} from your checking account to your savings account")
        elif account_type == "savings":
            new_checking_balance = checking_balance + amount
            new_savings_balance = savings_balance - amount
            add_user_transaction(username, f"({proper_datetime}) - Transferred ${amount} from your savings account to your checkings account")

        username = session['username']
        update_user_balance(username, "checking", new_checking_balance)
        update_user_balance(username, "savings", new_savings_balance)

        return render_template("transfer.html", checking_balance=new_checking_balance, savings_balance=new_savings_balance, message=f"Transferred ${amount} from your {account_type} account to your other account")
    
    return render_template("transfer.html", checking_balance=checking_balance, savings_balance=savings_balance)