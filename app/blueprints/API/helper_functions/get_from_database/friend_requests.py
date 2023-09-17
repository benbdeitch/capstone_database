
from app.blueprints.API.helper_functions.get_from_database.reading_history import get_reading_history
from app.blueprints.API.helper_functions.get_from_database.reading_list import get_reading_list
from app.models import  FriendRequest, User
from app import db


def get_friend_requests(user):
    friend_requests = {"in": [], "out": []}

    inc_friend_requests =  db.session.query(FriendRequest.fromUser, FriendRequest.toUser, User.username, FriendRequest.date).join(FriendRequest, FriendRequest.fromUser == User.id).filter_by(toUser = user.id).all()
    for requests in inc_friend_requests:
       friend_requests["in"].append({"from": requests.username, 'date': requests.date})

    #Accessing Outgoing Friend Requests: 
    out_friend_requests =  db.session.query(FriendRequest.fromUser, FriendRequest.toUser, User.username, FriendRequest.date).join(FriendRequest, FriendRequest.toUser == User.id).filter_by(fromUser = user.id).all()
    for requests in out_friend_requests:
        friend_requests["out"].append({"to": requests.username, 'date': requests.date})
    return friend_requests