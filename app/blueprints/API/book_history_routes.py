
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import bp as api
from app.models import FriendList, User, BookList, Book, BookHistory
from app import db

import requests






#This route adds a book to an account's reading history, optionally accepting a rating, and a review, but requiring the googleId. 
@api.post('/add-history')
@jwt_required()
def add_to_history():
    data = request.json
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    try:
        googleId = data["googleId"]
    except:
        return jsonify({"Error": "Please provide a valid id for the book."}), 400
    if "rating" not in data.keys():
        rating = None;
    else:
        rating = data["rating"]
    if "review" not in data.keys():
        review =  None;
    else:
        review = data["review"]
    book = Book.query.filter_by(googleId = googleId).first()
    if not book:
        book =add_to_database(googleId)
        if not book:
            return jsonify({"Error": f'Book id "{googleId}" could not be found.'}), 400
    entry_in_history = BookHistory.query.filter_by(userId = user.id, bookId = book.id).first()
    if entry_in_history:
        return jsonify({"Error": f'Book {book.title} is already in list.'})
    history_entry = BookHistory(userId = user.id, bookId = book.id, rating = rating, review = review)
    history_entry.commit()
    return jsonify({"Success": f'Book {book.title} added to reading history. '}), 200
        



@api.get('/history/<other_user>')
@jwt_required()
def get_history(other_user):
    username = get_jwt_identity();
    user = User.query.filter_by(username = username).first()
    if username == other_user:
         response = {"history": []}
         history = db.session.query(Book.id, Book.title, Book.author, Book.googleId, Book.publishDate, Book.image, BookHistory.review, BookHistory.rating).join(Book, BookHistory.bookId == Book.id).filter(BookHistory.userId== user.id).all()
         for query in history:
             book_review = {"title": query.title, "author": query.author, "googleId": query.googleId, "publishDate": query.publishDate, "image": query.image, "review": query.review, "rating": query.rating}
             response["history"].append(book_review)
         return jsonify(response), 200
    user = User.query.filter_by(username = username).first()
    searchee = User.query.filter_by(username = other_user).first()
    if not searchee:
         return jsonify({"Error": f'User {other_user} not found. '})
    if searchee.id < user.id:
        is_friend = FriendList.query.filter_by(userIdLower = searchee.id, userIdHigher = user.id).first()
    else: 
        is_friend = FriendList.query.filter_by(userIdHigher = searchee.id, userIdLower = user.id).first()
    if not is_friend:
        return jsonify({"Error": f'Cannot access the reading list of {searchee.username} without being friends.'}), 400
    response = {"history": []}
    history = db.session.query(Book.id, Book.title, Book.author, Book.googleId, Book.publishDate, Book.image, BookHistory.review, BookHistory.rating).join(Book, BookHistory.bookId == Book.id).filter(BookHistory.userId== searchee.id).all()
    for query in history:
        book_review = {"title": query.title, "author": query.author, "googleId": query.googleId, "publishDate": query.publishDate, "image": query.image, "review": query.review, "rating": query.rating}
        response["history"].append(book_review)
    return jsonify(response), 200
        



#helper function:
def add_to_database(googleId):
    data = requests.get(F'https://www.googleapis.com/books/v1/volumes/{googleId}').json()
    if "error" in data.keys():
        return False
    book = Book(title = data["volumeInfo"]["title"], author = data["volumeInfo"]["authors"][0] if "authors" in data["volumeInfo"].keys() else None, image = data["volumeInfo"]["imageLinks"]["thumbnail"] if "imageLinks" in data["volumeInfo"].keys() else None, publishDate = data["volumeInfo"]["publishedDate"] if "publishedDate" in data["volumeInfo"].keys() else None, googleId = googleId)
    book.commit()
    return book