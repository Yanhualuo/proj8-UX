# Laptop Service
import os
import pymongo
from flask import Flask, request, session, render_template, url_for, redirect
from flask_restful import Resource, Api
from pymongo import MongoClient
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer \
                          as Serializer, BadSignature, \
                          SignatureExpired)
import time
from pymongo import MongoClient
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length, AnyOf
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect

# Instantiate the app
csrf = CSRFProtect()

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'Thisisasecret!'
csrf.init_app(app)

client = MongoClient()
db = client.time
mongo = client.user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

auth = HTTPBasicAuth()

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


#############################################
def hash_password(password):
    return pwd_context.encrypt(password)


def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)


def generate_auth_token(expiration=600):
    # s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    # pass index of user
    return s.dumps({'id': 1})

def verify_auth_token(token):
    s = Serializer('test1234@#$')
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    return "Success"


#############################################

class ListAll(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]

        result = { 'open_time': [item["open_times"] for item in i],
        'close_time': [item["close_times"] for item in i],
        'km': [item["km"] for item in i]
        }
        return result


class ListAllJson(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
        
        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        doc = []
        for item in i:
            item_doc = {
                'km': item["km"],
                'open_time' : item["open_times"],
                'close_time': item["close_times"]
            }
            doc.append(item_doc)
        return doc


class ListAllCsv(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
        
        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]

        result=[]
        
        for item in i:
            temp = item["km"] + ", " + item["open_times"] + ", " + item["close_times"]
            result.append(temp)
            
        return result



###################################################


class ListOpenOnly(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result = { 'open_time': [item["open_times"] for item in i]}
        return result

class ListOpenOnlyJson(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100

        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result = []
        for item in i:
            item_doc = {
                'open_time' : item["open_times"]
            }
            result.append(item_doc)

        return result

class ListOpenOnlyCsv(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
    
        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result=[]
        
        for item in i:
            temp = item["open_times"]
            result.append(temp)
        return result


#################################


class ListCloseOnly(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
        item_list = db.tododb.find().sort("close_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result = { 'close_time': [item["close_times"] for item in i]}
        return result


class ListCloseOnlyJson(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100

        item_list = db.tododb.find().sort("close_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result = []
        for item in i:
            item_doc = {
                'close_time' : item["close_times"]
            }
            result.append(item_doc)
        return result


class ListCloseOnlyCsv(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100

        item_list = db.tododb.find().sort("close_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result=[]
        
        for item in i:
            temp = item["close_times"]
            result.append(temp)

        return result


# Create routes

api.add_resource(ListAll, '/listAll')
api.add_resource(ListAllJson, '/listAll/json')
api.add_resource(ListAllCsv, '/listAll/csv')

api.add_resource(ListOpenOnly, '/listOpenOnly')
api.add_resource(ListOpenOnlyJson, '/listOpenOnly/json')
api.add_resource(ListOpenOnlyCsv, '/listOpenOnly/csv')

api.add_resource(ListCloseOnly, '/listCloseOnly')
api.add_resource(ListCloseOnlyJson, '/listCloseOnly/json')
api.add_resource(ListCloseOnlyCsv, '/listCloseOnly/csv')

####################################################################################

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



# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
