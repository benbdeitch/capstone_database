from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from . import auth_routes, create_routes, get_routes, friend_routes, book_request_routes, google_routes, book_history_routes, delete_routes