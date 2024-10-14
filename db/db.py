from mysql.connector import connect, Error
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# print(sys.path)
from config.config import Config
# print(f"Current working directory: {os.getcwd()}")

def get_db_connection():
    try:
        connection = connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        print("MySQL connection successful.")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Call the function to test the connection
get_db_connection()