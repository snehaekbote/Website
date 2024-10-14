import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import Config

# Fetch environment variables
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"

def test_database_connection():
    try:
        print(f"DATABASE_URL: {DATABASE_URL}")  # Debugging line
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            assert connection is not None
    except OperationalError as e:
        pytest.fail(f"SQLAlchemy connection error: {e}")
    except Exception as e:
        pytest.fail(f"An error occurred: {e}")

