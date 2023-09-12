from datetime import date
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import bp as api
from app.models import User, BookList, Book, BookRequests
from app import db
from sqlalchemy import and_
import requests


#Accepts a request with {"toUsername": <target user's username, "googleId": <book's googleId>, "message": <optional message for the recipient}
@api.post('/recommend-book')
@jwt_required()
def recommend_book():
    data = request.json
    from_user = User.query.filter_by(username = get_jwt_identity()).first()
    try: 
        target_user = data["toUsername"]
        google_id = data["googleId"]
        message = data["message"][0:300]

    except:
        return jsonify({"Error": "Improperly formatted request."}), 400
    recipient = User.query.filter_by(username = target_user).first()
    if recipient:
        book = Book.query.filter_by(googleId = google_id).first()
        if not book:
            book = add_to_database(google_id)
            if not book:
                return jsonify({"Error": "No book found"}), 401
            bookId = book.id
            title = book.title
        new_request = BookRequests(toId = recipient.id, fromId =from_user.id, shortMessage = message, bookId = book.id, date = date.today())
        new_request.commit()
        return jsonify({"Success": f'Book {book.title} recommended to {target_user}.'}), 200
    return jsonify({"Error": f'User {target_user} not found in database. '})


@api.get('/my-recommendations')
@jwt_required()
def get_my_recommendations():
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    recommendations = db.session.query(Book.id, Book.title, Book.author, Book.googleId, Book.publishDate, Book.image, BookRequests.toId, BookRequests.fromId, BookRequests.shortMessage, BookRequests.date, BookRequests.index).join(Book, BookRequests.bookId == Book.id).filter(BookRequests.toId == user.id).all()

  
    response = {"recommendations": {"in":[], "out":[]}}
    
      #Accessing incoming Recommendations: 
    recommendations = db.session.query(BookRequests.fromId, Book.googleId, Book.title, Book.author, Book.image, Book.publishDate, BookRequests.toId, BookRequests.date, BookRequests.shortMessage, BookRequests.bookId, User.username).join(User, User.id == BookRequests.fromId).join(Book, Book.id == BookRequests.bookId).filter(BookRequests.toId == user.id).all()
    for books in recommendations: 
        response["recommendations"]["in"].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'author': books.author, 'publishDate': books.publishDate, 'image': books.image}, 'from': books.username, 'msg': books.shortMessage, 'date': books.date} )

    #accessing outgoing recommendations:
    out_recommendations = db.session.query(BookRequests.fromId, Book.googleId, Book.title, Book.author, Book.image, Book.publishDate, BookRequests.toId, BookRequests.date, BookRequests.shortMessage, BookRequests.bookId, User.username).join(User, User.id == BookRequests.toId).join(Book, Book.id == BookRequests.bookId).filter(BookRequests.fromId == user.id).all()
    for books in recommendations: 
         response["recommendations"]["out"].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'author': books.author, 'publishDate': books.publishDate, 'image': books.image}, 'to': books.username, 'msg': books.shortMessage, 'date': books.date} )
    return jsonify(response), 200





#Accepts a request with  {"index": <index>}
@api.post('/accept-rec')
@jwt_required()
def accept_recommendation():
    data = request.json
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    rec = BookRequests.query.filter_by(index = data["index"]).first()
    if not rec: 
        return jsonify({"Error": f'Recommendation #{data["index"]} does not exist.'})
    if rec.toId != user.id:
        return jsonify({"Error": f'Request #{data["index"]} is not associated with your account.'}), 400
    book_to_read = BookList(userId = user.id, bookId = rec.bookId, recommendedBy= rec.fromId)
    book_to_read.commit()
    rec.delete() 
    return jsonify({"Success": "Recommendation accepted."})


#Accepts a request with  {"index": <index>}
@api.post('/deny-rec')
@jwt_required()
def deny_recommendation():
    data = request.json
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    rec = BookRequests.query.filter_by(index = data["index"]).first()
    if not rec: 
        return jsonify({"Error": f'Recommendation #{data["index"]} does not exist.'})
    if rec.toId != user.id:
        return jsonify({"Error": f'Request #{data["index"]} is not associated with your account.'}), 400
    rec.delete()
    return jsonify({"Success": "Recommendation deleted."})


#helper function:
def add_to_database(googleId):
    data = requests.get(F'https://www.googleapis.com/books/v1/volumes/{googleId}').json()
    if "error" in data.keys():
        return False
    book = Book(title = data["volumeInfo"]["title"], author = data["volumeInfo"]["authors"][0] if "authors" in data["volumeInfo"].keys() else None, image = data["volumeInfo"]["imageLinks"]["thumbnail"] if "imageLinks" in data["volumeInfo"].keys() else None, publishDate = data["volumeInfo"]["publishedDate"] if "publishedDate" in data["volumeInfo"].keys() else None, googleId = googleId)
    book.commit()
    return book