from flask import Flask, render_template, session, request, redirect, jsonify 
import random 
import math
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector
import re, os
from peewee import MySQLDatabase, IntegerField

app = Flask(__name__)
mysql = MySQL(app)
app.secret_key = 'thisIsSecret'
random_decimal = random.randrange(0,100)

MYSQL_ROOT_USER = os.getenv('MYSQL_ROOT_USER', 'root')
MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD', 'admin')
MYSQL_ROOT_HOST = os.getenv('MYSQL_ROOT_HOST', 'mysql-service.default.svc.cluster.local')
MYSQL_ROOT_PORT = os.getenv('MYSQL_ROOT_PORT', '3306')
MYSQL_ROOT_DB = os.getenv('MYSQL_ROOT_DB', 'mydb')
FLASK_APP_PORT = os.getenv('FLASK_APP_PORT', '5000')

app.config['MYSQL_HOST'] = MYSQL_ROOT_HOST
app.config['MYSQL_PORT'] = int(MYSQL_ROOT_PORT)
app.config['MYSQL_USER'] = MYSQL_ROOT_USER
app.config['MYSQL_PASSWORD'] = MYSQL_ROOT_PASSWORD
app.config['MYSQL_DB'] = MYSQL_ROOT_DB

@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = 'Welcome!'
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            # session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect('/home')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = 'Welcome'
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
		        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (%s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
	session["victory"] = 0
	return render_template('guess.html')

@app.route('/process', methods=['POST'])
def process():
	if request.form.get('low'):
		low = int(request.form['low'])
		high = int(request.form['high'])
		randomValue = int(random.randint(low, high))
		Guesses = round(math.log(randomValue + 1, 2))

		if high - low < 9:
			Message = ("Thats to easy! The offset between the numbers needs to atleast be 10")
			return jsonify({'inputError' : Message})
		else:
			session['random_value'] = randomValue
			session['guess_value'] = Guesses
			guessLeft = str(session['guess_value'])
			print(session)

			Message = ("You've only " + str(Guesses)  + " chances to guess the integer!")
			return jsonify({'set' : Message, 'lowest' : low, 'highest' : high, 'guesses' : guessLeft})

	if request.form.get('guess'):
		guess = int(request.form['guess'])

		if session['random_value'] == guess:
			session['victory'] += 1
			score = session['victory']
			Message = ("Correct! The number was: " + str(guess))
			return jsonify({'won' : Message, 'score': score})

		elif session['random_value'] > guess:
			session['guess_value'] -= 1
			if session['guess_value'] == 0:
				session['victory'] -= 1
				score = session['victory']
				Message = ("Sadly you ran out of guesses, the number was " + str(session['random_value']) + ". please try again ")
				return jsonify({'error' : Message, 'guesses' : '0', 'score': score})
			else:
				Message = (str(guess) + " is to low! You have " + str(session['guess_value']) + " left")
				guessLeft = str(session['guess_value'])
				return jsonify({'wrong' : Message, 'guesses' : guessLeft})

		elif session['random_value'] < guess:
			session['guess_value'] -= 1
			if session['guess_value'] == 0:
				session['victory'] -= 1
				score = session['victory']
				Message = ("Sadly you ran out of guesses, the number was " + str(session['random_value']) + ". please try again ")
				return jsonify({'error' : Message, 'guesses' : '0', 'score': score})
			else:
				Message = (str(guess) + " is to high! You have " + str(session['guess_value'])  + " left")
				guessLeft = str(session['guess_value'])
				return jsonify({'wrong' : Message, 'guesses' : guessLeft})

	return jsonify({'error' : 'Some data is missing, please try again!'})

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)