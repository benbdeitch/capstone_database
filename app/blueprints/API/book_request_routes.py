from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import bp as api
from app.models import User, BookList, Book, BookRequests
from app import db
from sqlalchemy import and_


#Accepts a request with {"toUsername": <target user's username, "bookId": <book's id>, "message": <optional message for the recipient}
@api.post('/recommend-book')
@jwt_required()
def recommend_book():
    data = request.json
    from_user = User.query.filter_by(username = get_jwt_identity()).first()
    try: 
        target_user = data["toUsername"]
        book_id = data["bookId"]
        message = data["message"]

    except:
        return jsonify({"Error": "Improperly formatted request."}), 400
    recipient = User.query.filter_by(username = target_user).first()
    if recipient:
        book = Book.query.filter_by(id = book_id).first()
        if book:
            new_request = BookRequests(toId = recipient.id, fromId =from_user.id, shortMessage = message, bookId = book_id)
            new_request.commit()
            return jsonify({"Success": f'Book {book.title} recommended to {target_user}.'}), 200
        return jsonify({"Error": f'Book {book_id} not found in database.'}), 400
    return jsonify({"Error": f'User {target_user} not found in database. '})


@api.get('/my-recommendations')
@jwt_required()
def get_my_recommendations():
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    recommendations = db.session.query(Book.id, Book.title, Book.author, Book.publishDate, Book.image, BookRequests.toId, BookRequests.fromId, BookRequests.shortMessage, BookRequests.index).join(Book, BookRequests.bookId == Book.id).filter(BookRequests.toId == user.id).all()

  
    response = {"recommendations": []}
    for query in recommendations:
        from_name = User.query.filter_by(id = query.fromId).first()
        response["recommendations"].append({"from": from_name.username, "title": query.title, "author": query.author, "message": query.shortMessage, "publishDate": query.publishDate, "image": query.image, "requestId": query.index})
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
    book_to_read = BookList(userId = user.id, bookId = rec.bookId)
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