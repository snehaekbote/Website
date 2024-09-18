# import pytest
# from sqlalchemy import create_engine
# from sqlalchemy.exc import OperationalError
# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from config.config import Config

# DATABASE_URL = f"mysql+pymysql://admin:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"

# def test_database_connection():
#     try:
#         engine = create_engine(DATABASE_URL)
#         with engine.connect() as connection:
#             assert connection is not None
#     except OperationalError as e:
#         pytest.fail(f"SQLAlchemy connection error: {e}")
#     except Exception as e:
#         pytest.fail(f"An error occurred: {e}")

def test_hello_world():
    greeting = "Hello, World!"
    assert greeting == "Hello, World!"