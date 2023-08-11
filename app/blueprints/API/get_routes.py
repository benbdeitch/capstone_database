from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import bp as api
from app.models import User, BookList, Book, BookRequests
from app import db


#Currently returns a user's username and email. May later be integrated with the 'get friend's reading list' function.
@api.get('/user-profile/<user>')
@jwt_required()
def user_profile(user):
   print(user)
   user1 = User.query.filter_by(username = user).first()
   if user:

      return jsonify({ 'username':user, 'email':user1.email}), 200
   return jsonify(message='Invalid Username'), 404



#Gets a user's own reading list. 
@api.get('/get-book-list')
@jwt_required()
def get_book_list():
   username = get_jwt_identity()
   user = User.query.filter_by(username = username).first()
   if user:
      booklist = {"books":[]}
      list = db.session.query(Book.id, Book.title, Book.author, Book.publishDate, Book.image, BookList.priority).join(Book, BookList.bookId == Book.id).filter(BookList.userId == user.id).all()

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
   return jsonify({"Error": "User Not Found"}), 400

