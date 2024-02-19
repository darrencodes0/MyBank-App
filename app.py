import json
from flask import Flask, render_template, request, redirect, session, url_for
from user_info import load_user_info, authenticate_user, save_user_info
from user_transactions import add_transaction, load_user_transactions
from datetime import datetime
from sessionkey import SESSION_KEY

try:
    user_info = load_user_info()
except FileNotFoundError:
    user_info = []

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SESSION_KEY
    date_time = datetime.now()
    proper_datetime = date_time.strftime("%H:%M | %Y-%m-%d")

    @app.route("/", methods=["GET", "POST"])
    def start():
        return render_template("frontpage.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
                username = request.form.get("username")
                password = request.form.get("password")
                authenticated = authenticate_user(user_info, username, password)

                if authenticated:
                    session['username'] = username
                    return redirect(url_for('accountPage'))
                else:
                    return render_template("login.html",message="Login failed, Please check your user credentials")

        return render_template("login.html")

    
    @app.route("/registration", methods=["GET", "POST"])
    def registration():
        message = None
        if request.method == "POST":
            new_username = request.form.get("username")
            new_password = request.form.get("password")

            for user_data in user_info:
                if user_data["username"].lower() == new_username.lower():
                    return render_template("register.html", message="Username is already taken")

            if new_password:
                user_info.append({"username": new_username, "password": new_password, "balance": 0, "loan": 0})
                save_user_info(user_info)
                return redirect(url_for("login"))
            else:
                return render_template("register.html", message="Password is not provided")

        return render_template("register.html")


    @app.route("/accountpage", methods=["GET"])
    def accountPage():
        username = session.get('username')
        current_balance = 0
        for user_data in user_info:
            if user_data["username"] == username:
                loan = user_data["loan"]
                session['loan'] = loan
                current_balance = user_data["balance"]
                session['balance'] = current_balance
                break

        return render_template("accountpage.html", user=username, current_balance=current_balance, loan=loan)

    @app.route("/logout")
    def logout():
        # Clear the session data related to the user
        session.pop('username', None)
        session.pop('balance', None)
        return redirect(url_for('start'))

    @app.route("/deposit", methods=["GET", "POST"])
    def deposit():
        current_balance = session.get('balance')
        if request.method == "POST":
            amount = request.form.get("amount")

            if float(amount):
                amount = float(amount)  # Convert to a float
                for user_data in user_info:
                    if user_data["username"] == session['username']:
                        user_data["balance"] += amount
                        current_balance = user_data["balance"]
                        current_balance = round(current_balance, 2) # Round to 2 decimal places
                        session['balance'] = current_balance
                        save_user_info(user_info)  # Save the updated user information to the JSON file
                        add_transaction(session['username'],f"({proper_datetime}) - Deposited $" + str(amount) + " into your bank account")
                        return render_template("deposit.html", current_balance=current_balance, message="Deposited $" + str(amount) + " into your bank account")
                return render_template("deposit.html", current_balance=current_balance, message="message 404: User not found")
            else:
                return render_template("deposit.html", current_balance=current_balance, message="Incorrect input")

        return render_template("deposit.html", current_balance=current_balance)

    @app.route("/withdraw", methods=["GET", "POST"])
    def withdraw():
        current_balance = session.get('balance')
        if request.method == "POST":
            amount = request.form.get("amount")

            if float(amount):
                amount = float(amount)  # Convert to a float
                for user_data in user_info:
                    if user_data["username"] == session['username']:
                        if amount <= user_data["balance"]:
                            user_data["balance"] -= amount
                            current_balance = user_data["balance"]
                            current_balance = round(current_balance, 2) # Round to 2 decimal places
                            session['balance'] = current_balance
                            save_user_info(user_info)  # Save the updated user information to the JSON file
                            add_transaction(session['username'],f"({proper_datetime}) - Withdrawn $" + str(amount) + " from your bank account")
                            return render_template("withdrawal.html", current_balance=current_balance, message="Withdrawn $" + str(amount) + " from your bank account")
                        else:
                            return render_template("withdrawal.html", current_balance=current_balance, message="Insufficient Balance")
                return render_template("withdrawal.html", current_balance=current_balance, message="message 404, USER NOT FOUND")
            else:
                return render_template("withdrawal.html", current_balance=current_balance, message="Incorrect Input")

        return render_template("withdrawal.html", current_balance=current_balance)
    
    @app.route("/transactions")
    def transactions():
        username = session.get('username')
        user_transactions = load_user_transactions(username)
        return render_template("transactions.html", transactions=user_transactions)

    @app.route("/loans")
    def loans():
        username = session.get('username')

        for user_data in user_info:
            if user_data["username"] == username:
                loan_amount = user_data.get("loan",0)
                break

        return render_template("loans.html")

    
    @app.route("/pay_loan", methods=["GET", "POST"])
    def pay_loan():
        current_balance = session.get('balance')
        loan = session.get('loan')
        if request.method == "POST":
            amount = request.form.get("amount")

            if float(amount):
                amount = float(amount)  # Convert to a float
                for user_data in user_info:
                    if user_data["username"] == session['username']:
                        if amount == loan and amount <= user_data["balance"]:
                            user_data["balance"] -= amount
                            user_data["loan"] -= amount
                            current_balance = user_data["balance"]
                            current_balance = round(current_balance, 2) # Round to 2 decimal places
                            session['balance'] = current_balance
                            session['loan'] = 0
                            loan = session['loan']
                            save_user_info(user_info)
                            add_transaction(session['username'],f"({proper_datetime}) - " + "Paid $" + str(amount) + " loans off")
                            return render_template("pay_loan.html", current_balance=current_balance, message="Paid $" + str(amount) + " loans off",loan=loan)
                        elif amount <= user_data["balance"] and amount <= loan:
                            user_data["balance"] -= amount
                            user_data["loan"] -= amount
                            current_balance = user_data["balance"]
                            loan = user_data["loan"]
                            current_balance = round(current_balance, 2) # Round to 2 decimal places
                            loan = round(loan, 2)
                            session['loan'] = loan
                            session['balance'] = current_balance
                            save_user_info(user_info)  # Save the updated user information to the JSON file
                            add_transaction(session['username'],f"({proper_datetime}) - " + "Paid $" + str(amount) + " loans off")
                            return render_template("pay_loan.html", current_balance=current_balance, message="Paid $" + str(amount) + " loans off",loan=loan)
                        else:
                            return render_template("pay_loan.html", current_balance=current_balance, message="Cannot pay more than loan amount or insufficient funds",loan=loan)
                return render_template("pay_loan.html", current_balance=current_balance, message="message 404, USER NOT FOUND",loan=loan)
            else:
                return render_template("pay_loan.html", current_balance=current_balance, message="Incorrect Input",loan=loan)

        return render_template("pay_loan.html", current_balance=current_balance, loan=loan)
    

    @app.route("/request_loan", methods=["GET", "POST"])
    def request_loan():
        current_balance = session.get('balance')
        loan = session.get('loan')

        if request.method == "POST":
            amount = request.form.get("amount")

            if float(amount):
                amount = float(amount)  # Convert to a float
                for user_data in user_info:
                    if user_data["username"] == session['username']:
                        user_data["balance"] += amount
                        user_data["loan"] += amount + (0.25 * amount) # 25% set interest rate to loan added
                        current_balance = user_data["balance"]
                        loan = user_data["loan"]
                        current_balance = round(current_balance, 2) # Round to 2 decimal places
                        loan = round(loan, 2)
                        session['balance'] = current_balance
                        session['loan'] = loan
                        save_user_info(user_info)  # Save the updated user information to the JSON file
                        add_transaction(session['username'],f"({proper_datetime}) - Added $" + str(amount) + " in loans to your bank account")
                        return render_template("request_loan.html", current_balance=current_balance,message="Added $" + str(amount) + " in loans to your bank account",loan=loan)
                return render_template("request_loan.html", current_balance=current_balance,message="message 404: User not found",loan=loan)
            else:
                return render_template("request_loan.html", current_balance=current_balance,message="Incorrect input",loan=loan)

        return render_template("request_loan.html", current_balance=current_balance,loan=loan)
   
    
    return app
