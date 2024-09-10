import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

DATABASE_URL = "mysql+pymysql://admin:Admin#235@13.234.113.49/turtu_website"

def test_database_connection():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            assert connection is not None
    except OperationalError as e:
        pytest.fail(f"SQLAlchemy connection error: {e}")
    except Exception as e:
        pytest.fail(f"An error occurred: {e}")
