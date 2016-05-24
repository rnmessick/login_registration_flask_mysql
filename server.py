from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
# imports the Bcrypt module
from flask.ext.bcrypt import Bcrypt
import re
EMAIL_REGEX =re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
app = Flask(__name__)
mysql = MySQLConnector(app, 'login_registration_db')
bcrypt = Bcrypt(app)
app.secret_key = 'ThisIsSecret'

@app.route("/", methods=["GET"])
def index():
	return render_template('index.html')
@app.route("/process", methods=["POST"])
def registration():
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	email = request.form['email']
	password = request.form['password']
# run validations and if they are successful we can create the password hash with bcrypt
	pw_hash = bcrypt.generate_password_hash(password)
# now we insert the new user into the database
	insert_query = "INSERT INTO users (first_name, last_name, email, pw_hash, created_at, updated_at) VALUES (:first_name, :last_name, :email, :pw_hash, NOW(), NOW())"
	query_data = { 'first_name': first_name, 'last_name':last_name, 'email': email, 'pw_hash': pw_hash }
	mysql.query_db(insert_query, query_data)
# redirect to success page
	if len(request.form['first_name']) < 2 or len(request.form['last_name']) < 2:
		flash("Name must be greater than 2 letters!")
		return redirect("/")
	if (request.form['first_name']).isalpha() == False or (request.form['last_name']).isalpha() == False:
		flash("Name cannot contain any numbers.")
	if len(request.form["email"]) < 1:
		flash("Email cannot be blank!")
	elif not EMAIL_REGEX.match(request.form["email"]):
		flash("Invalid Email Address!")
	if len(request.form["password"]) < 8:
		flash("Invalid Password. Try again.")
	elif (request.form["password"]) != (request.form["confirm"]):
		flash("Passwords do not match.")
	else:
		flash("Thank you for registering")

	return redirect("/")
@app.route('/success', methods=['POST'])
def login():
	email = request.form['email']
	password = request.form['password']
	user_query = "SELECT * FROM users WHERE email = :email LIMIT 1"
	query_data = { 'email': email }
	user = mysql.query_db(user_query, query_data) # user will be returned in a list
	email = mysql.query_db(user_query, query_data)[0]
	if bcrypt.check_password_hash(user[0]['pw_hash'], password):
		return render_template("welcome_page.html", email=email)
	else:
		flash("Invalid Password. Please try again.")
		return redirect('/')
app.run(debug=True)