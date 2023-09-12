from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, unset_jwt_cookies
from sqlalchemy import or_

from app.blueprints.API.helper_functions import get_account_data
from . import bp as api
from app.models import FriendList, User, BookList, Book
from app import db
import re 

#accepts a request with {"username": <desired username>, "password": <desired password>, "email": <desired email address>}. If username or email are shared with a pre-existing user, no account will be created.
#Returns an access token, as though the user just signed in.
@api.post('/register')
def register():
    content, response = request.json, {}
    print(content)
    valid = True;
    content["username"] = content["username"].strip()[0:30]
    content["email"] = content["email"].lower()
    if User.query.filter_by(email=content['email']).first():
      response['email error']=f'{content["email"]} is already taken/ Try again'
      valid = False;
    if User.query.filter_by(username=content['username']).first():
      response['username error']=f'{content["username"]} is already taken/ Try again'
      valid = False;
    if 'password' not in content:
       response['message'] = "Please include password"
       valid;
    allow_username= re.compile('^[A-Za-z0-9_]{5,30}$')
    if not allow_username.search(content['username']):
      response['username validity error'] = f'{content["username"]} is an invalid username. Please pick a username that is only letters, numbers, and underscores, and is between 5-30 characters in length.'
      valid = False;
    allow_email=re.compile('^[a-z0-9]+@[a-z]+\.[a-z]{2,3}$');
    if not allow_email.search(content['email']):
       response['email validity error'] = f'{content["email"]} is an invalid email.'
       valid = False;
    if valid:
        u = User(username = content["username"], email = content["email"])
        print(u)
        
        u.hash_password(content["password"])
        u.commit()
        access_token = create_access_token(identity = content["username"])
        return jsonify({'Success': f'User account created for {u.username}.', "access_token": str(access_token)})
    else:
        return jsonify(response), 400
    

#Accepts a request with {"username": <user's username>, "password": <user's password>}. Returns an access token that is used for verification by JWT, along with the other information used by the program.
@api.post('/signin')
def sign_in():
   username, password = request.json.get('username').strip(), request.json.get('password')
   user = User.query.filter_by(username=username).first()
   if user and user.check_password(password):
      response = get_account_data(user)
      response["token"] = create_access_token(identity=username)
      response["username"] = username
      response["email"] = user.email
      return jsonify(response), 200
   else:
      return jsonify({'Error':'Invalid Username or Password / Try Again'}), 400



   
#Requires no input, and unsets the Access Token you were using. 
@api.post('/logout')
def logout():
   response = jsonify({'Success':'Successful Logout'})
   unset_jwt_cookies(response)
   return response

@api.post('/check')
@jwt_required()
def check_token():
   return jsonify({"msg": "Successful authentication"}), 200