


import requests

from app.models import Book


def add_to_database(googleId):
    data = requests.get(F'https://www.googleapis.com/books/v1/volumes/{googleId}').json()
    if "error" in data.keys():
        return False
    book = Book(title = data["volumeInfo"]["title"], author = data["volumeInfo"]["authors"][0] if "authors" in data["volumeInfo"].keys() else None, subtitle = data["volumeInfo"]["subtitle"], image = data["volumeInfo"]["imageLinks"]["thumbnail"] if "imageLinks" in data["volumeInfo"].keys() else None, small_image = data["volumeInfo"]["imageLinks"]["smallThumbnail"] if "imageLinks" in data["volumeInfo"].keys() else None, publishDate = data["volumeInfo"]["publishedDate"] if "publishedDate" in data["volumeInfo"].keys() else None, googleId = googleId)
    book.commit()
    return book