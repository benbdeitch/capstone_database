from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import bp as api
from app.models import User, BookList, Book




#This method is used for updating the 'priority' of books in the booklist. It accepts a list of objects with two keys, "googleID", and "priority". It sets the priority value of each book with matching googleID to the appropriate priority, which will be used in displaying them in order, on the webpage. 
@api.post('/update_priority')
@jwt_required()
def update_priority():
    data = request.json
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    if "items" in data:
        for item in data["items"]:
           book_id = Book.query.filter_by(googleId = item["googleId"]).first().id
           reading_list = BookList.query.filter(BookList.userId == user.id, BookList.bookId == book_id).first()
           reading_list.update_priority(item["priority"])
        return jsonify({"Success":"Hello"})
    else:
        return jsonify({"Error": "Invalid request made"}), 400