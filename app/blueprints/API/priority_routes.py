from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import bp as api
from app.models import User, BookList, Book, BookRequests
from app import db



#This method is used for updating the 'priority' of books in the booklist. It accepts a list of objects with two keys, "googleID", and "priority". It sets the priority value of each book with matching googleID to the appropriate priority, which will be used in displaying them in order, on the webpage. 
@api.put('/update_priority')
@jwt_required()
def update_priority():
    data = request.json
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    if data.get("items"):
        user_book_list = BookList.query.filter_by(userId = user.id).all()
        print (user_book_list)
        #for book in data["items"]:
        return jsonify({"Success":"Hello"})
    else:
        return jsonify({"Error": "Invalid request made"}), 400