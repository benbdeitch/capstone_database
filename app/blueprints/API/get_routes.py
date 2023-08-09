from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import bp as api
from app.models import User, BookList, Book, BookRequests




@api.get('/user-profile')
@jwt_required()
def user_profile():
   username = get_jwt_identity()
   user = User.query.filter_by(username = username).first()
   if user:
      user_data = user.to_dict()
      return jsonify({ 'user': user_data}), 200
   return jsonify(message='Invalid Username'), 404
