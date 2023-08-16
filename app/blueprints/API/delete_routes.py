from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import bp as api
from app.models import User, Book, BookList, BookRequests, FriendRequest
from requests import get


#deletes a book from a user's reading list, without adding it to history.
#Requires an input with the "googleId" key.
@api.post('/delete-list')
@jwt_required()
def delete_from_list():
    data = request.json
    try:
        id =  data["googleId"]
    except:
        return jsonify({"Error": "Improperly formatted request"}), 400
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    if user:
        book = Book.query.filter_by(googleId = id).first()
        if book:
            book_to_delete = BookList.query.filter_by(userId = user.id,bookId = book.id).first()
            if book_to_delete:
                book_to_delete.delete()
                return jsonify({"Success": f'Book id "{id}" deleted from list.'}), 200
            return jsonify({"Error": f'Book id "{id}" not found in user\'s reading list.'}), 400
        return jsonify({"Error": f'Book id "{id}" not found in database'}), 400
    return jsonify({"Error": "User authentication failed."})   