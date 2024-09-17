from flask import Flask, g, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
from config.config import Config
from models.models import db, User
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.data_routes import data_bp, create_engine_from_config, export_multiple_tables_to_excel
from dotenv import load_dotenv
from flask_cors import CORS
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import signal
import os
import atexit
import threading

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from Config class

# CORS(app)# This will enable CORS for all routes
CORS(app, origins=["http://13.234.113.49","http://13.235.115.160","http://13.201.168.191"])



# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Register the blueprint
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(data_bp, url_prefix='/api')
# print(app.url_map)

@app.before_request
def load_logged_in_user():
    email = session.get('email')  # Get the email from session
    if email:
        g.user = User.query.filter_by(email=email).first()  # Load user from DB
    else:
        g.user = None

# Function to handle the automated export
def automated_export():
    engine = create_engine_from_config()
    if engine:
        tables = ["career_applications", "contacts", "users"]  # Replace with your actual table names
        excel_file = "api_export_automated.xlsx"
        export_multiple_tables_to_excel(engine, tables, excel_file)

# Set up APScheduler for automated tasks
scheduler = BackgroundScheduler()
scheduler.add_job(func=automated_export, trigger="interval", minutes=1)  # Runs every 1 minute
scheduler.start()

# Handle shutdown signals (like Ctrl+C) gracefully
def shutdown_scheduler(signum, frame):
    print("Shutting down gracefully...")
    scheduler.shutdown()
    print("Scheduler successfully shut down.")

# Catch the shutdown signal (Ctrl+C)
signal.signal(signal.SIGINT, shutdown_scheduler)
signal.signal(signal.SIGTERM, shutdown_scheduler)

@app.route('/test_db')
def test_db_connection():
    try:
        # Test database connection
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return "Successfully connected to the database!"
    except Exception as e:
        return f"Failed to connect to the database. Error: {e}"
    
# @app.route('/test')
# def test_route():
#     return "Test route works!"



if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except (KeyboardInterrupt, SystemExit):
        shutdown_scheduler(None, None) 