import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv('DEBUG') == 'True'


    # Add DB_CONFIG dictionary
    DB_CONFIG = {
        'host': DB_HOST,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'database': DB_NAME
    }

# Debugging output to verify variables
print("DB_HOST:", Config.DB_HOST)
print("DB_USER:", Config.DB_USER)
print("DB_PASSWORD:", Config.DB_PASSWORD)  # This should now print "Admin#235"
