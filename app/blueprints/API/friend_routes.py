from . import bp as api
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import User, FriendRequest, FriendList
from app import db
from flask import request, jsonify




@api.post('/make-request')
@jwt_required()
def make_friend_request():
     data= request.json
     username = get_jwt_identity()
     user = User.query.filter_by(username = username).first()
     if user: 
         try: 
             friend = data["username"]
         except:
             return jsonify({"Error": "Incorrectly formatted request"}), 400
         toUser = User.query.filter_by(username = friend).first()
         if toUser:
            alreadyMade = FriendRequest.query.filter_by(fromId = user.Id, toId = toUser.id).first()
            if alreadyMade:
                return jsonify({"Error": "Friend Request already made"})
            lowerId  = user.id if (user.id < toUser.id) else toUser.id
            higherId = user.id if lowerId == toUser.id else toUser.id
            alreadyFriends = FriendList.query.filter_by(userIdLower = lowerId, userIdHigher = higherId)
            if alreadyFriends:
                return jsonify({"Error": f'You are already friends with {friend}'})
            newRequest = FriendRequest(toId = toUser.id, fromId = user.id)
            newRequest.commit()
            return jsonify({"Success": f'Friend {friend} has been added.'}), 200
         else:
             return jsonify({"Error": f'User {friend} not found on the database.'})
     else: 
         return jsonify({"Error": "Request must be made from a valid account."})
     




@api.get('/get-<friend>-list')
@jwt_required()
def get_friend_list(friend):
   username = get_jwt_identity()
   user = User.query.filter_by(username = username).first()
   if user:
      pass