from sqlalchemy import or_
from app import db
from app.models import Book, BookList, FriendList, User


#This function is for swiftly accessing the majority of the account's information. It is used when initially loading the webpage, and when manually refreshing it, to handle desyncs between the browser and database. 
def get_account_data(user):
   #Setting up the initial response
   response = {'username': '', 'token':'', 'friends':{}, 'friendRequests': [], 'readingList':[], 'readingHistory':[], }


    #Accessing the user's reading list. 
   reading_list = db.session.query(BookList.dateAdded, Book.id, Book.googleId, Book.title, Book.author, Book.publishDate, Book.image, BookList.priority, User.username).outerjoin(User, BookList.recommendedBy == User.id).join(Book, BookList.bookId == Book.id).filter(BookList.userId == user.id).all()
   for books in reading_list:
         response['readingList'].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'author': books.author, 'publishDate': books.publishDate, 'image': books.image}, 'dateAdded': books.dateAdded, 'priority': books.priority, 'from':books.username })
   #Accesses the Friend's list
   allFriends = FriendList.query.filter(or_(FriendList.userIdLower== user.id, FriendList.userIdHigher == user.id)).all()
   

   for query in allFriends:
      friend_id = query.userIdLower if query.userIdLower!= user.id else query.userIdHigher
      friend = User.query.filter_by(id = friend_id).first()
      response["friends"].update({friend.username: {"email": friend.email, "date": query.date}})
   
   return response