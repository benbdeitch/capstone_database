from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.blueprints.API.helper_functions import get_account_data
from . import bp as api
from app.models import User, BookList, Book, BookRequests
from app import db


#Currently returns a user's username and email. May later be integrated with the 'get friend's reading list' function.
@api.get('/user-profile/<user>')
@jwt_required()
def user_profile(user):
   print(user)
   user1 = User.query.filter_by(username = user).first()
   if user1:

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
      reading_list = db.session.query(BookList.dateAdded, Book.id, Book.googleId, Book.title, Book.author, Book.publishDate, Book.image, BookList.priority).join(Book, BookList.bookId == Book.id).filter(BookList.userId == user.id).all()

      if reading_list:
         print(reading_list)
         for i in range(len(reading_list)):
            book = {"date": reading_list[i].dateAdded, "title": reading_list[i].title,
                 "author": reading_list[i].author,
                 "publishDate":  reading_list[i].publishDate,
                  "image": reading_list[i].image,
                  "priority": str(reading_list[i].priority),
                  "id": str(i),
                   "googleId": reading_list[i].googleId }
            booklist["books"].append(book)
         return jsonify(booklist), 200
      return jsonify({"Message": "Empty List"})
   return jsonify({"Error": "User Not Found"}), 400


#Refreshes the whole local storage for the browser.
@api.get('/refresh')
@jwt_required()
def refresh():
   username = get_jwt_identity()
   user = User.query.filter_by(username = username).first()
   response = get_account_data(user)
   return jsonify(response), 200