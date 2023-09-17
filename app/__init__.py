from flask import  Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from datetime import timedelta




app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)
CORS(app)
jwt = JWTManager(app)


app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours = 1)
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = "asf32KVs9324KSWO"  # Change this in your code!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)


login_manager = LoginManager(app)
login_manager.login_view = 'auth.sign_in'
login_manager.login_message = 'Please log in, before continuing'
login_manager.login_message_category = 'warning'

from app.blueprints.API import bp as api
app.register_blueprint(api)
from app import models