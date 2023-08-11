from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import bp as api
from app.models import User, Book, BookList, BookRequests, FriendRequest
from requests import get


#Placeholder route-- will eventually be replaced by integration with the google book api. 
@api.post('/add-book')
def add_book():
    data = request.json

    book_title = request.json["title"]
    author = request.json["author"]
    image = request.json["image"]
    publishDate = request.json["pubdate"]
    if not Book.query.filter_by(title = book_title, author = author).first():

        book = Book(title = book_title, author = author, image = image, publishDate = publishDate)
        book.commit();

        return jsonify({"Success": f'"{book.title}" has been added.'})
    return jsonify({"Error": f'Book "{book_title}" by {author} is already in the database.'})



#Route for adding books to the user's reading list. Requires an input of {"priority": <value to indicate ordering on the reading list.>, "id": <book's id number in the database.> }
@api.post('/add-book-list')
@jwt_required()
def add_book_list():
    data = request.json
    if not data["priority"]:
        priority = 0
    elif data["priority"].isdecimal():
        priority = int(data["priority"])
    else:
        priority = 0
    
    username = get_jwt_identity()
    user = User.query.filter_by(username = username).first()
    already_in = BookList.query.filter_by(userId = user.id, bookId = data["id"] ).first()
    if already_in:
        return jsonify({"Error": "Book is already present within the list. "}), 400
    if not user:
        return  jsonify({"Error": f'{username} account does not exist. Please ensure you are using a proper key.'}), 400
    book = Book.query.filter_by(id = data["id"]).first()
    if not book:
        return jsonify({"Error": f'Book id#{data["id"]} does not exist. Please try again'}), 400
    
    addition = BookList(bookId = data["id"], userId = user.id, priority = priority );
    addition.commit();
    return jsonify({"Success": f'Book #{data["id"]} has been added.'}), 200

