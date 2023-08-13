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


