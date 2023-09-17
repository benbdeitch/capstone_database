

from app.models import  User, BookRequests, Book
from app import db

#This function accesses both the incoming and outgoing recommendations for a given user. 
def get_recommendations(user):
    recommendations= {"in":[], "out": []}

    #Accessing
    in_recommendations = db.session.query(BookRequests.fromId, Book.googleId, Book.title, Book.subtitle, Book.author, Book.image, Book.small_image, Book.publishDate, BookRequests.toId, BookRequests.date, BookRequests.shortMessage, BookRequests.bookId, User.username).join(User, User.id == BookRequests.fromId).join(Book, Book.id == BookRequests.bookId).filter(BookRequests.toId == user.id).all()
    for books in in_recommendations: 
        recommendations["in"].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'subtitle': books.subtitle, 'author': books.author, 'publishDate': books.publishDate, 'image': {'img':books.image,'imgSml': books.imgSml}}, 'from': books.username, 'msg': books.shortMessage, 'date': books.date} )

    out_recommendations = db.session.query(BookRequests.fromId, Book.googleId, Book.title, Book.subtitle, Book.author, Book.image, Book.small_image, Book.publishDate, BookRequests.toId, BookRequests.date, BookRequests.shortMessage, BookRequests.bookId, User.username).join(User, User.id == BookRequests.toId).join(Book, Book.id == BookRequests.bookId).filter(BookRequests.fromId == user.id).all()
    for books in out_recommendations: 
        recommendations["out"].append({'book':{ 'googleId': books.googleId, 'title': books.title, 'subtitle': books.subtitle, 'author': books.author, 'publishDate': books.publishDate, 'image': {'img':books.image,'imgSml': books.small_image}}, 'to': books.username, 'msg': books.shortMessage, 'date': books.date} )


    return recommendations