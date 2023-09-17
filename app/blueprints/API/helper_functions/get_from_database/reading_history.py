from flask_jwt_extended import create_access_token
import requests
from sqlalchemy import or_
from app import db
from app.models import Book, BookHistory, BookList, BookRequests, FriendList, FriendRequest, User



#This accesses the PostgreSQL database, in order to return the associated history with a user's reading list. 
def get_reading_history(user):
    user_history = []
    reading_history = db.session.query(BookHistory.date, Book.id, Book.title, Book.subtitle, Book.author, Book.googleId, Book.publishDate, Book.image, Book.small_image, BookHistory.review, BookHistory.rating).join(Book, BookHistory.bookId == Book.id).filter(BookHistory.userId== user.id).all()
    for books in reading_history:
       user_history.append({'book':{ 'googleId': books.googleId, 'title': books.title, 'subtitle': books.subtitle, 'author': books.author, 'publishDate': books.publishDate, 'image': {'img':books.image,'imgSml': books.small_image}}, "review": books.review, "rating": books.rating, "date": books.date})
    return user_history