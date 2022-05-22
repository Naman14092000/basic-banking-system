from crypt import methods
import email
from threading import currentThread
from flask import Flask, render_template, request, jsonify, redirect, url_for
from  flask_cors import CORS, cross_origin
from pymongo import MongoClient
import time
import random
app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.banking_db
users = db.users
accounts = db.accounts
transactions = db.transactions
email = ""
CORS(app, supports_credentials=True)

@app.route('/')
@cross_origin(origins='*',supports_credentials=True)
def login_page():
    return render_template('login.html')

@app.route('/logout')
def logout():
    global email
    email = ""
    return render_template('login.html')
@app.route('/homepage')
def homepage():
    global email
    return render_template('index.html', email = email)

@app.route('/transactionhistory')
def transactionhistory():
    if email == "":
        redirect(url_for('login_page'))
    else:
        allTransactionsForUser = []
        for x in transactions.find({}, {'sender': email}):
            currentTransaction = {}
            currentTransaction['sender'] = x['sender']
            currentTransaction['receiver'] = x['receiver']
            currentTransaction['amount'] = x['amount']
            allTransactionsForUser.append(currentTransaction)
        for x in transactions.find({}, {'receiver': email}):
            currentTransaction = {}
            currentTransaction['sender'] = x['sender']
            currentTransaction['receiver'] = x['receiver']
            currentTransaction['amount'] = x['amount']
            allTransactionsForUser.append(currentTransaction)
        return render_template('transactionhistory.html', transactions = allTransactionsForUser)

@app.route('/transfermoneypage')
def transfermoneypage():
    try:
        if email == "":
            redirect(url_for('login_page'))
        else:    
            allUsers = []
            for x in  users.find({'email': {'$ne': email}}):
                currentUser = {}
                currentUser['email'] = x['email']
                currentUser['name'] = x['name']
                currentUser['balance'] = x['balance']
                currentUser['id'] = x['_id']
                allUsers.append(currentUser)
            return render_template('transfermoney.html', users = allUsers)
    except Exception as e:
        return render_template('error.html', error = e)
@app.route('/transfermoney', methods=['POST'])
def transfermoney():
    try:
        if email == "":
            redirect(url_for('login_page'))
        else:
            sender = request.form['sender']
            receiver = request.form['receiver']
            amount = request.form['amount']
            dateTime = time.asctime(time.localtime(time.time()))
            transactions.insert_one({'sender': sender, 'receiver': receiver, 'amount': amount, 'dateTime': dateTime})
            return redirect(url_for('homepage'))
    except:
        return render_template('error.html', error = "Money could not be transferred due to technical error")
@app.route('/sendmoneypage')
def sendmoneypage():
    try:
        global email
        if email == "":
            redirect(url_for('login_page'))
        else:
            user = users.find_one({'email': email})
            print(user)
            allUsers = []
            for x in  users.find({'email': {'$ne': email}}):
                currentUser = {}
                currentUser['email'] = x['email']
                currentUser['name'] = x['name']
                currentUser['balance'] = x['balance']
                currentUser['id'] = x['_id']
                allUsers.append(currentUser)
            print(allUsers)
            return render_template('selecteduserdetails.html', user = user, users = allUsers)
    except Exception as e:
        return render_template('error.html', error = e)

@app.route('/sendMoney', methods=['POST'])
def sendMoney():
    try:
        if request.method == 'POST':
            for key,value in request.form.items():
                print(key, value)
            to = request.form['to']
            amount = request.form['amount']
            global email
            print(email)
            user = users.find_one({'email': email})
            transactions.insert_one({'sender': user['name'], 'receiver': to, 'amount': amount})
            myquery = {"email": email}
            newvalues = {"$set": {'balance': int(user['balance']) - int(amount)}}
            users.update_one(myquery, newvalues)
            myquery = {"name": to}
            user = users.find_one({'name': to})
            newvalues = {"$set": {'balance': int(user['balance']) + int(amount)}}
            users.update_one(myquery, newvalues)
            return redirect(url_for('homepage'))
    except Exception as e:
        return render_template('error.html', error = e)
@app.route('/login', methods=['POST'])
def login():
    try:
        print(users.count_documents({'email': request.form['email'], 'password': request.form['password']}))
        if users.count_documents({'email': request.form['email'], 'password': request.form['password']}) > 0:
            global email
            email = request.form['email']
            return render_template('index.html', email=request.form['email'])
        else:
            return render_template('error.html', error = "Account with given credentials not found.")
    except Exception as e:
        print(e)
        return render_template('error.html', error = e)
@app.route('/register', methods=['POST'])
def register():
    try:
        name = request.form['name']
        emailToRegister = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirm_password']
        if(password == confirmPassword):
            if users.count_documents({'email':emailToRegister, 'password': password}) > 0:
                return render_template('error.html', error = "User already registered")                
            else:
                balance = random.randint(0,9) * 10000 + random.randint(0,9) * 1000 + random.randint(0,9) * 100 + random.randint(0,9) * 10 + random.randint(0,9)
                users.insert_one({'name': name, 'email': emailToRegister, 'password': password, 'balance': balance})
                global email
                email = request.form['email']
                return render_template('index.html', email = email)
    except Exception as e:
        print(e)
        return render_template('error.html', error = e)


@app.route('/register_page')
def register_page():
    return render_template('signup.html')
