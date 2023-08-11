from flask import request, jsonify
from flask_jwt_extended import create_access_token, unset_jwt_cookies
from . import bp as api
from app.models import User

#accepts a request with {"username": <desired username>, "password": <desired password>, "email": <desired email address>}. If username or email are shared with a pre-existing user, no account will be created.
#Returns an access token, as though the user just signed in.
@api.post('/register')
def register():
    content, response = request.json, {}
    print(content)
    if User.query.filter_by(email=content['email']).first():
      response['email error']=f'{content["email"]} is already taken/ Try again'
    if User.query.filter_by(username=content['username']).first():
      response['username error']=f'{content["username"]} is already taken/ Try again'
    if 'password' not in content:
       response['message'] = "Please include password"
    
    try:
        u = User(username = content["username"], email = content["email"])
        print(u)
        
        u.hash_password(content["password"])
        u.commit()
        access_token = create_access_token(identity = content["username"])
        return jsonify({'Success': f'User account created for {u.username}.', "access_token": str(access_token)})
    except:
        return jsonify(response), 400
    

#Accepts a request with {"username": <user's username>, "password": <user's password>}. Returns an access token that is used for verification by JWT. 
@api.post('/signin')
def sign_in():
   username, password = request.json.get('username'), request.json.get('password')
   user = User.query.filter_by(username=username).first()
   if user and user.check_password(password):
      access_token = create_access_token(identity=username)
      return jsonify({'access_token':access_token}), 200
   else:
      return jsonify({'Error':'Invalid Username or Password / Try Again'}), 400


#Requires no input, and unsets the Access Token you were using. 
@api.post('/logout')
def logout():
   response = jsonify({'Success':'Successful Logout'})
   unset_jwt_cookies(response)
   return response
