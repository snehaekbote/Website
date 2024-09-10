from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Replace with your actual connection string
DATABASE_URL = "mysql+pymysql://admin:Admin#235@13.234.113.49/turtu_website"

try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("Connection to MySQL database was successful!")
    connection.close()
except OperationalError as e:
    print(f"SQLAlchemy connection error: {e}")
except NameError as e:
    print(f"Error: {e}")
