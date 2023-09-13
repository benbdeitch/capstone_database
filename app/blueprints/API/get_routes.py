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
      reading_list = db.session.query(BookList.dateAdded, Book.id, Book.googleId, Book.title, Book.author, Book.publishDate, Book.image, Book.small_image, BookList.priority, User.username).outerjoin(User, BookList.recommendedBy == User.id).join(Book, BookList.bookId == Book.id).filter(BookList.userId == user.id).all()
   
      if reading_list:
         print(reading_list)
         reading_list.sort(reverse = True, key =lambda item: item.priority)
         for books in reading_list:
            booklist['books'].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'author': books.author, 'publishDate': books.publishDate, 'image': {"image": books.image, "thumbnail": books.smallImage}}, 'dateAdded': books.dateAdded, 'priority': books.priority, 'from':books.username })

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