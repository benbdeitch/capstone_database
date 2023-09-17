from sqlalchemy import or_
from app.blueprints.API.helper_functions.get_from_database.reading_history import get_reading_history
from app.blueprints.API.helper_functions.get_from_database.reading_list import get_reading_list
from app.models import FriendList, User

#This function accesses the user's friends list, and returns the data. It also accesses the friend's reading list, and reading history. 
def get_friends(user):
    friends = {}
    allFriends = FriendList.query.filter(or_(FriendList.userIdLower== user.id, FriendList.userIdHigher == user.id)).all()
    for query in allFriends:
        friend_id = query.userIdLower if query.userIdLower!= user.id else query.userIdHigher
        friend = User.query.filter_by(id = friend_id).first()



        friends.update({friend.username: {"email": friend.email, "date": query.date, "readingList": get_reading_list(friend), "readingHistory": get_reading_history(friend)}})
    return(friends)