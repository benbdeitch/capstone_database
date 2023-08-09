from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from random import randint

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

    id = db.Column(db.Integer(), primary_key = True)
    title = db.Column(db.String(), nullable = False)
    author = db.Column(db.String(), nullable = False)
    image = db.Column(db.String(), nullable = False)
    publishDate = db.Column(db.String(), nullable = False)


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

    def commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class BookList(db.Model):
    index = db.Column(db.Integer(), primary_key = True)
    userId = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    bookId = db.Column(db.Integer(), db.ForeignKey('book.id'), nullable = False)
    priority = db.Column(db.Integer())

    def commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class bookBlackList(db.Model):
    index = db.Column(db.Integer(), primary_key = True)
    userId = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    bookId = db.Column(db.Integer(), db.ForeignKey('book.id'), nullable = False)

    def commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()