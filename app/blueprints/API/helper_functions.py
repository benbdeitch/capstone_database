from flask_jwt_extended import create_access_token
from sqlalchemy import or_
from app import db
from app.models import Book, BookHistory, BookList, BookRequests, FriendList, FriendRequest, User


#This function is for swiftly accessing the majority of the account's information. It is used when initially loading the webpage, and when manually refreshing it, to handle desyncs between the browser and database. 
def get_account_data(user):
   #Setting up the initial response
   response = { 'username': "", 'token': "", 'email': "", 'friends':{}, 'friendRequests': [], 'readingList':[], 'readingHistory':[], 'recommendations':[]}

    #Accessing the user's reading list. 
   reading_list = db.session.query(BookList.dateAdded, Book.id, Book.googleId, Book.title, Book.author, Book.publishDate, Book.image, BookList.priority, User.username).outerjoin(User, BookList.recommendedBy == User.id).join(Book, BookList.bookId == Book.id).filter(BookList.userId == user.id).all()
   for books in reading_list:
         response['readingList'].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'author': books.author, 'publishDate': books.publishDate, 'image': books.image}, 'dateAdded': books.dateAdded, 'priority': books.priority, 'from':books.username })


    #Accessing the user's Reading History.

   reading_history = db.session.query(BookHistory.date, Book.id, Book.title, Book.author, Book.googleId, Book.publishDate, Book.image, BookHistory.review, BookHistory.rating).join(Book, BookHistory.bookId == Book.id).filter(BookHistory.userId== user.id).all()
   for books in reading_history:
       response['readingHistory'].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'author': books.author, 'publishDate': books.publishDate, 'image': books.image}, "review": books.review, "rating": books.rating, "date": books.date})

   #Accesses the Friend's list
   allFriends = FriendList.query.filter(or_(FriendList.userIdLower== user.id, FriendList.userIdHigher == user.id)).all()
   for query in allFriends:
      friend_id = query.userIdLower if query.userIdLower!= user.id else query.userIdHigher
      friend = User.query.filter_by(id = friend_id).first()

      friend_reading_list = db.session.query(User.username, Book.googleId, Book.title, Book.author, Book.publishDate, Book.image, BookList.priority, BookList.dateAdded).join(Book, BookList.bookId == Book.id).outerjoin(User, BookList.recommendedBy == User.id ).filter(BookList.userId == friend.id).all()
      
      response["friends"].update({friend.username: {"email": friend.email, "date": query.date, "readingList": [], "readingHistory": []}})
      for books in friend_reading_list:
         
          response["friends"][friend.username]["readingList"].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'author': books.author, 'publishDate': books.publishDate, 'image': books.image}, 'dateAdded': books.dateAdded, 'priority': books.priority, 'from':books.username })
      history = db.session.query(BookHistory.date, Book.id, Book.title, Book.author, Book.googleId, Book.publishDate, Book.image, BookHistory.review, BookHistory.rating).join(Book, BookHistory.bookId == Book.id).filter(BookHistory.userId== friend.id).all()
      for books in history:
          response["friends"][friend.username]["readingHistory"].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'author': books.author, 'publishDate': books.publishDate, 'image': books.image}, "review": books.review, "rating": books.rating, "date": books.date})
    
    #Accessing Recommendations: 
   recommendations = db.session.query(BookRequests.fromId, Book.googleId, Book.title, Book.author, Book.image, Book.publishDate, BookRequests.toId, BookRequests.date, BookRequests.shortMessage, BookRequests.bookId, User.username).join(User, User.id == BookRequests.fromId).join(Book, Book.id == BookRequests.bookId).filter(BookRequests.toId == user.id).all()
   for books in recommendations: 
        response["recommendations"].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'author': books.author, 'publishDate': books.publishDate, 'image': books.image}, 'from': books.username, 'msg': books.shortMessage, 'date': books.date} )


    #Accessing Friend Requests:
   friend_requests =  db.session.query(FriendRequest.fromUser, FriendRequest.toUser, User.username).join(FriendRequest, FriendRequest.fromUser == User.id).filter_by(toUser = user.id).all()
   for requests in friend_requests:
       response["friendRequests"].append({"from": requests.username})
   print(response)
   return response