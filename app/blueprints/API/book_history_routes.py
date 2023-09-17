
from datetime import date
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.blueprints.API.helper_functions.get_from_database.reading_history import get_reading_history
from app.blueprints.API.helper_functions.google_database.add_book_by_id import add_to_database
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
        if int(rating)<0:
            rating = 0;
        if float(rating)>int(10): 
            rating = 10;

    if "review" not in data.keys():
        review =  None;
    else:
        review = data["review"][0:10000]
    book = Book.query.filter_by(googleId = googleId).first()
    if not book:
        book =add_to_database(googleId)
        if not book:
            return jsonify({"Error": f'Book id "{googleId}" could not be found.'}), 400
    entry_in_history = BookHistory.query.filter_by(userId = user.id, bookId = book.id).first()
    if entry_in_history:
        return jsonify({"Error": f'Book {book.title} is already in list.'})
    history_entry = BookHistory(userId = user.id, bookId = book.id, rating = rating, review = review, date = date.today())
    history_entry.commit()
    entry_in_list = BookList.query.filter_by(userId = user.id, bookId = book.id).first()
    if entry_in_list:
        entry_in_list.delete()
    return jsonify({"Success": f'Book {book.title} added to reading history. '}), 200
        



@api.get('/history/<other_user>')
@jwt_required()
def get_history(other_user):
    username = get_jwt_identity();
    user = User.query.filter_by(username = username).first()
    if username == other_user:
         return jsonify({"history": get_reading_history(user)}), 200
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
    return jsonify( {"history": get_reading_history(searchee)}), 200
        

@api.delete('/history/delete')
@jwt_required()
def delete_history():
    data = request.json
    if not data["googleId"]:
        return jsonify({"Error": "Invalid information provided."}), 400
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    book_id = Book.query.filter_by(googleId= data["googleId"]).first().id
    review = BookHistory.query.filter_by(bookId = book_id, userId = user.id).first()
    if review:
        review.delete()
        return jsonify({"Msg": "Entry Deleted"}),200
    else:
        return jsonify({"Error": f'No entry with id {data["googleId"]} found. '}), 400


