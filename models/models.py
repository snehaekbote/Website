from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # New fields for OTP
    otp = db.Column(db.String(6), nullable=True)  # Store OTP as a string of 6 characters
    otp_expiry = db.Column(db.DateTime, nullable=True)  # Time when OTP expires
    email_verified = db.Column(db.Boolean, default=False)  # Track if email is verified

    def __init__(self, username, email, phone_number, password, otp=None, otp_expiry=None, email_verified=False):
        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.password = password
        self.otp = otp
        self.otp_expiry = otp_expiry
        self.email_verified = email_verified
        

    def __repr__(self):
        return f'<User {self.username}>'
    
class CareerApplication(db.Model):
    __tablename__ = 'career_applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    profile = db.Column(db.String(255), nullable=False)
    resume_filename = db.Column(db.String(255), nullable=False)  # Update column name to match DB

    def __init__(self, email, phone_number, profile, resume_filename):
        self.email = email
        self.phone_number = phone_number
        self.profile = profile
        self.resume_filename = resume_filename

    def __repr__(self):
        return f'<CareerApplication {self.email}>'


class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    queries = db.Column(db.String(500), nullable=False)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, email, phone_number, queries):
        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.queries = queries

    def __repr__(self):
        return f'<Contact {self.username}>'
