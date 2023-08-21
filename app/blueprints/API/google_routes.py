from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import bp as api
from app.models import User, BookList, Book, BookRequests
from app import db
from config import Config
import requests




#This route searches for a book in google's API database. It accepts objects with at least one of the following keys. 
#{"intitle": <section of the title>, "inauthor": <section of the author>}
@api.post('/book-search')
@jwt_required()
def search_book_from_google():
    data = request.json
    title, author, how_many_entries = "", "", 10
    if "howManyEntries" in data.keys():
         try:
           how_many_entries =  int(data["howManyEntries"])
         except:
            return jsonify({"Error": "A non integer number of entries was requested."}),400

    if "title" in data.keys() and data["title"]!=  "":
        title = '"' + data["title"] + '"'
    if "author" in data.keys() and data["author"]!= "":
        author = '"' + data["author"] + '"'
    if (title == "" and author == ""):
        return jsonify({"Error": "Request cannot be carried out, without at least one value for author or title."}), 400
    string = 'https://www.googleapis.com/books/v1/volumes?q=' + f'{"intitle:"  + title if title!= "" else "" }'
    string = string + f'{"inauthor:" + author if author!= "" else ""}'
    string = string + "&fields=totalItems,items/volumeInfo/title,items/volumeInfo/authors,items/volumeInfo/publishedDate,items/volumeInfo/imageLinks/thumbnail"
    string = string + f'&key={Config.GOOGLE_API_KEY}'
    data = requests.get(string).json()
    if data["totalItems"] == 0:
        return jsonify({"Error": "No items found."})
    found_books = {"books": []}
    for entry in data["items"]:
        book = {"googleId": entry["id"],
                "title": entry["volumeInfo"]["title"],
                "author":entry["volumeInfo"]["authors"][0] if "authors" in entry["volumeInfo"].keys() else "Unknown",
                "publishDate": entry["volumeInfo"]["publishedDate"] if "publishedDate" in entry["volumeInfo"].keys() else "No Date",
                "image": entry["volumeInfo"]["imageLinks"]["thumbnail"] if "imageLinks" in entry["volumeInfo"].keys() else "No Image"}
        found_books["books"].append(book)
        if len(found_books["books"]) >= how_many_entries or len(found_books["books"]) > 29:
            break;
    
    return jsonify(found_books), 200



#Seeks to add a book to the database.  Requires the google ID number of the volume that you wish to add, and optionally allows for priority. 
#If the book is present to the database, it attempts to add it to your reading list. Otherwise, it adds the book to the database, then adds it to your reading list. 
#It also allows for an optional 'toUser' key, which instead adds the book to another's reading list.
@api.post("add-book-list")
@jwt_required()
def add_book_list():
    data = request.json

    if "googleId" not in data.keys():
         return jsonify({"Error": "Incorrect request. No book ID provided for google's API."})
    googleId = data["googleId"]
    username = get_jwt_identity();
    user = User.query.filter_by(username = username).first()
    if "priority" not in data.keys():
            priority = 0
    elif data["priority"].isdecimal():
            priority = int(data["priority"])
    else:
            priority = 0
    alreadyHave = Book.query.filter_by(googleId = googleId).first()
    title = ""
    if alreadyHave:
        bookId = alreadyHave.id
        title = alreadyHave.title
    else:
         add_book = add_to_database(googleId)
         if not add_book:
            return jsonify({"Error": "No book found"}), 401
         bookId = add_book.id
         title = add_book.title
    alreadyInList = BookList.query.filter_by(userId = user.id, bookId = bookId).first()
    if alreadyInList:
         return jsonify({"Error": f'Book {title} already in user\'s reading list.'}), 400
    new_list = BookList(userId = user.id, bookId = bookId, priority = priority)
    new_list.commit();
    return jsonify({"Success": f'Book {title} successfully added.'}),200
    


#helper function:
def add_to_database(googleId):
    data = requests.get(F'https://www.googleapis.com/books/v1/volumes/{googleId}').json()
    if "error" in data.keys():
        return False
    book = Book(title = data["volumeInfo"]["title"], author = data["volumeInfo"]["authors"][0] if "authors" in data["volumeInfo"].keys() else None, image = data["volumeInfo"]["imageLinks"]["thumbnail"] if "imageLinks" in data["volumeInfo"].keys() else None, publishDate = data["volumeInfo"]["publishedDate"] if "publishedDate" in data["volumeInfo"].keys() else None, googleId = googleId)
    book.commit()
    return book


@api.get('/book/<googleId>')
@jwt_required()
def get_book_by_google_id(googleId):
   data = requests.get(F'https://www.googleapis.com/books/v1/volumes/{googleId}').json()
   if "error" in data.keys():
        return jsonify({"Error": "Book id {googleId} not found."}), 400
   else: 

         book = {"googleId": data["id"],
                "title": data["volumeInfo"]["title"],
                "author":data["volumeInfo"]["authors"][0] if "authors" in data["volumeInfo"].keys() else "Unknown",
                "publishDate": data["volumeInfo"]["publishedDate"] if "publishedDate" in data["volumeInfo"].keys() else "No Date",
                "image":data["volumeInfo"]["imageLinks"]["thumbnail"] if "imageLinks" in data["volumeInfo"].keys() else "No Image"}
         return jsonify(book),200
