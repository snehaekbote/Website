from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
from config.config import Config
from models.models import db
from routes.routes import routes_bp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from Config class

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Register the blueprint
app.register_blueprint(routes_bp)

@app.route('/test_db')
def test_db_connection():
    try:
        # Test database connection
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return "Successfully connected to the database!"
    except Exception as e:
        return f"Failed to connect to the database. Error: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
