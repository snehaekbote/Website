from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# class User(db.Model):
#     __tablename__ = 'users'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     username = db.Column(db.String(100), nullable=False, unique=True)
#     email = db.Column(db.String(100), nullable=False, unique=True)
#     phone_number = db.Column(db.String(20), nullable=False, unique=True)
#     password = db.Column(db.String(255), nullable=False)
#     # New fields for OTP
#     otp = db.Column(db.String(6), nullable=True)  # Store OTP as a string of 6 characters
#     otp_expiry = db.Column(db.DateTime, nullable=True)  # Time when OTP expires
#     email_verified = db.Column(db.Boolean, default=False)  # Track if email is verified

#     def __init__(self, username, email, phone_number, password, otp=None, otp_expiry=None, email_verified=False):
#         self.username = username
#         self.email = email
#         self.phone_number = phone_number
#         self.password = password
#         self.otp = otp
#         self.otp_expiry = otp_expiry
#         self.email_verified = email_verified
        
    
#     def __repr__(self):
#         return f'<User {self.username}>'
    
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    # New fields for OTP
    otp = db.Column(db.String(6), nullable=True)  # Store OTP as a string of 6 characters
    otp_expiry = db.Column(db.DateTime, nullable=True)  # Time when OTP expires
    
    # Use is_verified to track if the user has verified their email
    is_verified = db.Column(db.Boolean, default=False)  # Default to False until email is verified
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(10), default='user')  # 'user' or 'admin'
    


    def __init__(self, username, email, phone_number, password, otp=None, otp_expiry=None, is_verified=False,  registration_date=None, role='user'):
        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.password = password
        self.otp = otp
        self.otp_expiry = otp_expiry
        self.is_verified = is_verified
        self.registration_date = datetime.utcnow(),
        self.role=role
        
    
    def __repr__(self):
        return f'<User {self.username}>'

class CareerApplication(db.Model):
    __tablename__ = 'career_applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    profile = db.Column(db.String(255), nullable=False)
    resume_data = db.Column(db.LargeBinary, nullable=False)  # Storing the file as BLOB
    resume_filename = db.Column(db.String(255), nullable=False)  # Update column name to match DB
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  

    user = db.relationship('User', backref=db.backref('career_applications', lazy=True))

    def __init__(self, email, phone_number, profile, resume_data, resume_filename, user_id):
        self.email = email
        self.phone_number = phone_number
        self.profile = profile
        self.resume_data = resume_data
        self.resume_filename = resume_filename
        self.user_id = user_id

    def __repr__(self):
        return f'<CareerApplication {self.email}>'

def check_email_exists(email):
    # Query the User model to check if an email exists
    user = User.query.filter_by(email=email).first()
    return user is not None

class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    queries = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, email, phone_number, queries):
        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.queries = queries

    def __repr__(self):
        return f'<Contact {self.username}>'
