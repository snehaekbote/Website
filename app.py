
# from flask import Flask, g, session, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import text
# from flask_migrate import Migrate
# from config.config import Config
# from models.models import db, User
# from routes.auth_routes import auth_bp
# from routes.user_routes import user_bp
# # from routes.data_routes import data_bp, create_engine_from_config, export_multiple_tables_to_excel
# from dotenv import load_dotenv
# from flask_cors import CORS
# import pandas as pd
# from apscheduler.schedulers.background import BackgroundScheduler
# import signal
# import os
# import atexit
# import threading
# from werkzeug.exceptions import RequestEntityTooLarge

# # Load environment variables from .env file
# load_dotenv()

# app = Flask(__name__)
# app.config.from_object(Config)  # Load configuration from Config class


# # Fetch the origins from environment variables
# origins1 = os.getenv("ALLOWED_ORIGINS1").split(",")
# origins2 = os.getenv("ALLOWED_ORIGINS2").split(",")
# # Use CORS with the loaded origins
# CORS(app, origins1=origins1)
# CORS(app, origins2=origins2)
# CORS(app, resources={r"/api/*": {"origins": "https://server.turtu.in"}}, methods=["POST"])


# # Initialize SQLAlchemy
# db.init_app(app)

# # Initialize Flask-Migrate
# migrate = Migrate(app, db)

# # Set the maximum file size to 1 MB in the main app config
# app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB

# # Error handler for file size limit
# @app.errorhandler(RequestEntityTooLarge)
# def handle_file_too_large(e):
#     return jsonify({
#         'status': 'error',
#         'message': 'File size exceeds the maximum limit of 1 MB.'
#     }), 413

# # Register the blueprint
# app.register_blueprint(auth_bp, url_prefix='/api')
# app.register_blueprint(user_bp, url_prefix='/api')
# # app.register_blueprint(data_bp, url_prefix='/api')
# # print(app.url_map)


# @app.before_request
# def load_logged_in_user():
#     email = session.get('email')  # Get the email from session
#     if email:
#         g.user = User.query.filter_by(email=email).first()  # Load user from DB
#     else:
#         g.user = None

# # Function to handle the automated export
# # def automated_export():
# #     engine = create_engine_from_config()
# #     if engine:
# #         tables = ["career_applications", "contacts", "users"]  # Replace with your actual table names
# #         excel_file = "api_export_automated.xlsx"
# #         export_multiple_tables_to_excel(engine, tables, excel_file)

# # # Set up APScheduler for automated tasks
# # scheduler = BackgroundScheduler()
# # scheduler.add_job(func=automated_export, trigger="interval", minutes=1)  # Runs every 1 minute
# # scheduler.start()

# # # Handle shutdown signals (like Ctrl+C) gracefully
# # def shutdown_scheduler(signum, frame):
# #     print("Shutting down gracefully...")
# #     scheduler.shutdown()
# #     print("Scheduler successfully shut down.")

# # # Catch the shutdown signal (Ctrl+C)
# # signal.signal(signal.SIGINT, shutdown_scheduler)
# # signal.signal(signal.SIGTERM, shutdown_scheduler)

# @app.route('/test_db')
# def test_db_connection():
#     try:
#         # Test database connection
#         with db.engine.connect() as connection:
#             result = connection.execute(text("SELECT 1"))
#             return "Successfully connected to the database!"
#     except Exception as e:
#         return f"Failed to connect to the database. Error: {e}"
    
# # Get the port from the environment, default to 5000 if not set
# port = int(os.getenv("PORT"))

# if __name__ == '__main__':
#     # try:
#         app.run(host='0.0.0.0', port=port, debug=True)
#     # except (KeyboardInterrupt, SystemExit):
#     #     shutdown_scheduler(None, None) 



from flask import Flask, g, session, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
from config.config import Config
from models.models import db, User
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
import logging

# from routes.data_routes import data_bp, create_engine_from_config, export_multiple_tables_to_excel

from dotenv import load_dotenv
from flask_cors import CORS
import os

import atexit
import threading
from werkzeug.exceptions import RequestEntityTooLarge

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)


# Configure logging
logging.basicConfig(level=logging.INFO)

@app.errorhandler(500)
def internal_error(error):
    logging.exception("An error occurred during registration.")
    return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

# Fetch the origins from environment variables
origins1 = os.getenv("ALLOWED_ORIGINS1").split(",")
origins2 = os.getenv("ALLOWED_ORIGINS2").split(",")
combined_origins = origins1 + origins2

# Use CORS with combined origins
CORS(app, origins=combined_origins)

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)


# Set maximum file size to 1 MB in app config

# Set the maximum file size to 1 MB in the main app config
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB

# Error handler for file size limit
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({
        'status': 'error',
        'message': 'File size exceeds the maximum limit of 1 MB.'
    }), 413


# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')


# Register the blueprint
# app.register_blueprint(data_bp, url_prefix='/api')
# print(app.url_map)


@app.before_request
def load_logged_in_user():
    email = session.get('email')
    if email:
        g.user = User.query.filter_by(email=email).first()
    else:
        g.user = None


# Set custom CORS headers explicitly after each request
@app.after_request
def set_custom_headers(response):
    # Explicitly set the Access-Control-Allow-Private-Network header to false
    response.headers['Access-Control-Allow-Private-Network'] = 'false'
    return response

# Function to handle the automated export
# def automated_export():
#     engine = create_engine_from_config()
#     if engine:
#         tables = ["career_applications", "contacts", "users"]  # Replace with your actual table names
#         excel_file = "api_export_automated.xlsx"
#         export_multiple_tables_to_excel(engine, tables, excel_file)

# # Set up APScheduler for automated tasks
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=automated_export, trigger="interval", minutes=1)  # Runs every 1 minute
# scheduler.start()

# # Handle shutdown signals (like Ctrl+C) gracefully
# def shutdown_scheduler(signum, frame):
#     print("Shutting down gracefully...")
#     scheduler.shutdown()
#     print("Scheduler successfully shut down.")

# # Catch the shutdown signal (Ctrl+C)
# signal.signal(signal.SIGINT, shutdown_scheduler)
# signal.signal(signal.SIGTERM, shutdown_scheduler)


@app.route('/test_db')
def test_db_connection():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return "Successfully connected to the database!"
    except Exception as e:
        return f"Failed to connect to the database. Error: {e}"

port = int(os.getenv("PORT", 5000))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)

    


    

    # try:
    # except (KeyboardInterrupt, SystemExit):
    #     shutdown_scheduler(None, None) 

