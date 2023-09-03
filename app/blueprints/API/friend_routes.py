from datetime import date
from . import bp as api
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import User, FriendRequest, FriendList, Book, BookList
from app import db
from flask import request, jsonify
from sqlalchemy import or_



#Route for posing a friend request to another user. Input is {"username": <desired friend's username>}.
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
            alreadyMade = FriendRequest.query.filter_by(fromUser = user.id, toUser = toUser.id).first()
            print(alreadyMade)
            if alreadyMade:
                return jsonify({"Error": "Friend Request already made"})
            lowerId  = user.id if (user.id < toUser.id) else toUser.id
            higherId = user.id if lowerId == toUser.id else toUser.id
            alreadyFriends = FriendList.query.filter_by(userIdLower = lowerId, userIdHigher = higherId).first()
            if alreadyFriends:
                return jsonify({"Error": f'You are already friends with {friend}'})
            newRequest = FriendRequest(toUser = toUser.id, fromUser = user.id, date = date.today())
            newRequest.commit()
            return jsonify({"Success": f'Friend request has been sent to {friend}.'}), 200
         else:
             return jsonify({"Error": f'User {friend} not found on the database.'})
     else: 
         return jsonify({"Error": "Request must be made from a valid account."})
     

#Route for accepting a friend request from a user. Fails if there is no pending request from that user to accept.
@api.post('accept-request')
@jwt_required()
def accept_request():
    data = request.json
    try: 
        friend = data["username"]
    except:
        return jsonify({"Error": "Incorrectly formatted request"}), 400
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    if user:
        friendUser = User.query.filter_by(username = friend).first()
        if friendUser:
            isValidRequest = FriendRequest.query.filter_by(toUser = user.id, fromUser = friendUser.id).first()
            if isValidRequest:
                lowerId  = user.id if (user.id < friendUser.id) else friendUser.id
                higherId = user.id if lowerId == friendUser.id else friendUser.id
                newFriendRelation = FriendList(userIdLower = lowerId, userIdHigher = higherId, date = date.today())
                newFriendRelation.commit()
                isValidRequest.delete()

                return jsonify({"Success": f'User {username} is now friends with User {friend}'}), 200
            return jsonify({"Error": f'User {friend} must have sent User {username} a friend request, before it can be accepted.'}), 400
        return jsonify({"Error": f'User {friend} does not exist'}), 400
    return jsonify({"Error": "User's authentication failed. Please log in, and try again."}), 400


#Route for declining a sent friend request.
@api.post('/decline-request')
@jwt_required()
def decline_request():
    data = request.json
    try: 
        friend = data["username"]
    except:
        return jsonify({"Error": "Incorrectly formatted request"}), 400
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    if user:
        friendUser = User.query.filter_by(username = friend).first()
        if friendUser:
            activeRequest = FriendRequest.query.filter_by(fromUser = friendUser.id, toUser = user.id).first()
            if activeRequest:
                activeRequest.delete()
                return jsonify({"Success": f'Denied user request from {friend}'}), 200
            return jsonify({"Error": f'No active request from {friend}'}),400
        return jsonify({"Error": f'No user named {friend} found.'}),400
    return jsonify({"Error": "Login credentials invalid."}),400

#Returns a list of all friends that you have. Returns in the form of {"friends": <array of friend objects>}
#Friend objects, here, are {"username": <friend's username>, "email": <friend's email>}
@api.get('/all-friends')
@jwt_required()
def get_all_friends():
    print("Getting Friends")
    response = {"friends": []}
    username = get_jwt_identity();
    user = User.query.filter_by(username = username).first()
    allFriends = FriendList.query.filter(or_(FriendList.userIdLower== user.id, FriendList.userIdHigher == user.id )).all()
    if len(allFriends) == 0:
        return jsonify(response), 200
    friend_id_list = []
    for query in allFriends:
        friend_id_list.append(query.userIdLower if query.userIdLower!= user.id else query.userIdHigher)
    print(friend_id_list)
    
    for id in friend_id_list:
        friend = User.query.filter_by(id = id).first()
        response["friends"].append({"username": friend.username, "email": friend.email, "date": friend.date})
    return jsonify(response), 200



#Returns the reading list of a user's friend. The user must already be friends with the target user, for this to work. 
@api.get('/<friend>-reading-list')
@jwt_required()
def get_friend_list(friend):
   username = get_jwt_identity()
   user = User.query.filter_by(username = username).first()
   if user:
      friend_user = User.query.filter_by(username = friend).first()
      if friend_user:
          lowerId  = user.id if (user.id < friend_user.id) else friend_user.id
          higherId = user.id if lowerId == friend_user.id else friend_user.id
          isFriends = FriendList.query.filter_by(userIdLower= lowerId, userIdHigher = higherId).first()
          if isFriends:
              booklist = {"books":[]}
              list = db.session.query(Book.id, Book.title, Book.author, Book.publishDate, Book.image, BookList.priority).join(Book, BookList.bookId == Book.id).filter(BookList.userId == friend_user.id).all()

              if list:
                  print(list)
                  for i in range(len(list)):
                      book = {"title": list[i].title,
                 "author": list[i].author,
                 "publishDate":  list[i].publishDate,
                  "image": list[i].image,
                  "priority": str(list[i].priority),
                  "id": str(i) }
                      booklist["books"].append(book)
                  return jsonify(booklist), 200
              return jsonify({"Message": "Empty List"})
          return jsonify({"Error": f'User {username} and User {friend} are not friends.'}), 400
      return jsonify({"Error": f'User {friend} does not exist.'}), 400
   return jsonify({"Error": "User {username} authentication failed. "}), 400



#requires input with key 'username'. 
@api.post('/remove-friend')
@jwt_required()
def remove_friend():
    data = request.json
    try: 
        friend = data["username"]
    except:
        return jsonify({"Error": "Incorrectly formatted request"}), 400
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    if user: 
        friendUser= User.query.filter_by(username = friend).first()
        if friend:
            lowerId  = user.id if (user.id < friendUser.id) else friendUser.id
            higherId = user.id if lowerId == friendUser.id else friendUser.id
            isFriend = FriendList.query.filter_by(userIdLower = lowerId, userIdHigher = higherId).first()
            if isFriend:
                isFriend.delete()
                return jsonify({"Success": f'You are no longer friends with {friend}'}), 400
            return jsonify({"Error": f'Cannot remove {friend} from friends; you aren\'t friends with them in the first place.'}), 400
        return jsonify({"Error": f'Cannot find user "{friend}"'}), 400
    return jsonify({"Error": "Cannot access account, please ensure that you are logged in."})



@api.get('/isfriend/<other_user>')
@jwt_required()
def is_friend(other_user):
    username = get_jwt_identity()
    user= User.query.filter_by(username = username).first()
    friend = User.query.filter_by(username = other_user).first()
    if not friend:
        return jsonify({"Error": f'No such user "{friend}", exists.'}), 400
    if user.id < friend.id:
        lower_id, higher_id = user.id, friend.id
    else:
        lower_id, higher_id = friend.id, user.id
    isFriend = FriendList.query.filter_by(userIdLower = lower_id, userIdHigher = higher_id).first()
    if isFriend:
        return jsonify({"status": "friend"}), 200
    hasRequest = FriendRequest.query.filter_by(fromUser = user.id, toUser = friend.id).first()
    if hasRequest:
        return jsonify({"status": "requestMade"}), 200
    madeRequest = FriendRequest.query.filter_by(toUser = user.id, fromUser = friend.id).first()
    if madeRequest:
        return jsonify({"status": "madeRequest"}),200
    return jsonify({"status": "none"})



@api.get('/friend-requests')
@jwt_required()
def get_all_requests():
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    requests =  FriendRequest.query.filter_by(toUser = user.id).all()
    response = {"requests": []}
    for query in requests:
        other_user = User.query.filter_by(id = query.fromUser).first()
        response["requests"].append(other_user.username)
    return jsonify(response), 200