from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config.config import Config
from models.models import db, User
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.data_routes import data_bp
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration from Config class

    # CORS(app) - This will enable CORS for all routes
    CORS(app, origins=["http://13.234.113.49", "http://13.235.115.160", "http://13.201.168.191"])

    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(data_bp, url_prefix='/api')

    @app.before_request
    def load_logged_in_user():
        email = session.get('email')  # Get the email from session
        if email:
            g.user = User.query.filter_by(email=email).first()  # Load user from DB
        else:
            g.user = None

    return app
