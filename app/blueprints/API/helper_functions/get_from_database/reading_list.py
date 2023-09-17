from flask_jwt_extended import create_access_token
import requests
from sqlalchemy import or_
from app import db
from app.models import Book, BookHistory, BookList, BookRequests, FriendList, FriendRequest, User


#This function accesses the PostgreSQL database, and returns it as an array of 'book' objects. 
def get_reading_list(user):
    reading_list = db.session.query(BookList.dateAdded, Book.id, Book.googleId, Book.title, Book.subtitle, Book.author, Book.publishDate, Book.image, Book.small_image, BookList.priority, User.username).outerjoin(User, BookList.recommendedBy == User.id).join(Book, BookList.bookId == Book.id).filter(BookList.userId == user.id).all()
    reading_list = []
    for books in reading_list:
        reading_list.append({'book':{ 'googleId': books.googleId, 'title': books.title, 'subtitle': books.subtitle, 'author': books.author, 'publishDate': books.publishDate, 'image': {'img':books.image, 'imgSml': books.small_image}}, 'dateAdded': books.dateAdded, 'priority': books.priority, 'from':books.username })
    return reading_list