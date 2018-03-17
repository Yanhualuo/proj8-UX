import os
import pymongo
import time
from pymongo import MongoClient
from flask import Flask, render_template, url_for, redirect,request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length, AnyOf
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisisasecret!'
csrf.init_app(app)

client = MongoClient('db', 27017)
db = client.time
mongo = client.user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User():

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username



@login_manager.user_loader
def load_user(username):
	#u = app.config['USER_COLLECTION'].find_one({"_id": username})
	users = mongo.db.users
	u = users.find_one({"username": username})
	if not u:
		return None
	return User(u['username'])



class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired('A username is required!'), Length(min=1, max=10, message='Must be between 5 and 10 characters.')])
    password = PasswordField('password', validators=[InputRequired('Password is required!'), Length(min=1, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired('A username is required!'), Length(min=1, max=10, message='Must be between 5 and 10 characters.')])
    password = PasswordField('password', validators=[InputRequired('Password is required!'), Length(min=1, max=80)])


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():  
    form = LoginForm()
    if form.validate_on_submit():
    	users = mongo.db.users
    	print("all user: ", users)
    	user = users.find_one({"username": form.username.data})
    	print(user)
    	if user:
    		print("~~~check password: ", user['password'])
    		if check_password_hash(user['password'], form.password.data):
    			#print("hello world")
    		    user_obj = User(user['username'])

    		    login_user(user_obj, remember=form.remember.data)
    		    print("login !!!!!!!!!!!!!!!!!!!!!!!!!!")
    		    return redirect(url_for("dashboard"))
        #flash("Wrong username or password", category='error')
    return render_template('login.html', title='login', form=form)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm()
	users = mongo.db.users
	existing_user = users.find_one({'username' : form.username.data})
	if form.validate_on_submit():
		#return '<h1>The username is {}. The password is {}.'.format(form.username.data, form.password.data)
		if existing_user is None:
			hashed_pw = generate_password_hash(form.password.data, method='sha256')
			users.insert({'username': form.username.data, 'password':hashed_pw})
			print(" hash pw is " + hashed_pw)
			return '<h1>new user create</h1>'
		else:
			return '<h1> username taken</h1>'
	return render_template('signup.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html', name=current_user.username)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


