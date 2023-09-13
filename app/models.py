from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from random import randint
from datetime import date
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True, nullable = False)
    password_hash = db.Column(db.String(), nullable = False)
    email = db.Column(db.String(150), unique = True, nullable = False)


    def __repr__(self):
        return f'User { self.username}'
    
    def to_dict(self):
        return {"username": self.username, "email": self.email}
    
    def commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    #These two functions are used in tandem, to avoid storing plaintext passwords. 
    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Book(db.Model):

    #This table tracks stored book data, that other users have already requested from the Google API. 
    id = db.Column(db.Integer(), primary_key = True)
    subtitle = db.Column(db.String(), nullable = True)
    title = db.Column(db.String(), nullable = False)
    author = db.Column(db.String(), nullable = True)
    image = db.Column(db.String(), nullable = True)
    small_image = db.Column(db.String(), nullable=True)
    publishDate = db.Column(db.String(), nullable = True)
    googleId = db.Column(db.String())


    def commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class BookRequests(db.Model):
    index = db.Column(db.Integer(), primary_key = True)
    fromId = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    toId = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    bookId = db.Column(db.Integer(), db.ForeignKey('book.id'), nullable = False)
    shortMessage = db.Column(db.String(300), nullable = True)
    date = db.Column(db.Date(), nullable = False)


    def commit(self):

        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class BookList(db.Model):

    #This table tracks which users have given books on their respective reading lists. 

    index = db.Column(db.Integer(), primary_key = True)
    userId = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    bookId = db.Column(db.Integer(), db.ForeignKey('book.id'), nullable = False)
    priority = db.Column(db.Integer())
    dateAdded = db.Column(db.Date(), nullable = False)
    recommendedBy = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = True)
    def commit(self):
        db.session.add(self)
        db.session.commit()

    def update_priority(self, new_priority):
        self.priority = new_priority
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class BlacklistedBook(db.Model):

    #This table tracks the books that a given user has no interest in seeing requests of, again. 
    index = db.Column(db.Integer(), primary_key = True)
    userId = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    bookId = db.Column(db.Integer(), db.ForeignKey('book.id'), nullable = False)

    def commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class BookHistory(db.Model):

    #This table tracks the books that a User has read, and any review or rating that they have given them. 

    index = db.Column(db.Integer(), primary_key = True)
    userId = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    bookId = db.Column(db.Integer(), db.ForeignKey('book.id'), nullable = False)
    rating = db.Column(db.Integer(),  nullable = True)
    review = db.Column(db.String(10000), nullable = True)
    date = db.Column(db.Date(), nullable = False)

    def updateRating(self, rating):
        if rating <= 10 and rating >= 0:
            self.rating = rating
        self.commit();
    
    def updateReview(self, reviewString):
        self.review = reviewString;
        self.commit();
    def commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class UserBlackList(db.Model):

    
    index = db.Column(db.Integer(), primary_key = True)
    userId = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    blockedUserId  = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    dateBlocked = db.Column(db.Date(), nullable = False)

    def commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class FriendList(db.Model):
    index = db.Column(db.Integer(), primary_key = True)
    userIdLower = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    userIdHigher = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    date = db.Column(db.Date(), nullable = False)

    def commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class FriendRequest(db.Model):
    index = db.Column(db.Integer(), primary_key = True)
    toUser = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    fromUser = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    date = db.Column(db.Date(), nullable = False)


    def commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
