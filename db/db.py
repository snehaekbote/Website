from mysql.connector import connect, Error
from config.config import Config

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
