from flask import current_app , Blueprint, render_template, request, session, jsonify, url_for
import mysql.connector
from flask_login import login_required, current_user
from mysql.connector import IntegrityError
from db.db import get_db_connection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
import re
import pymysql
from datetime import datetime, timedelta
import pytz
from mysql.connector import Error
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import logging
import random
import jwt
from models.models import db, User, CareerApplication, Contact, check_email_exists
from functools import wraps
from utils.email_utils import send_otp_email, send_password_reset_email
from flask_cors import CORS
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from apscheduler.schedulers.background import BackgroundScheduler
from config.config import Config

auth_bp = Blueprint('auth', __name__)

# Define the timezone
tz = pytz.timezone('UTC')  # Or your local time zone
# Localize the datetime
now = datetime.now(tz)

# Define the secret key for encoding/decoding tokens (you should ideally keep this in your config)
SECRET_KEY = 'SECRET_KEY'



@auth_bp.route('/')
def home():
    return render_template('home.html')



# @auth_bp.route('/register', methods=['POST'])
# def register():
#     if request.method == 'POST':
#         username = request.json.get('username')
#         email = request.json.get('email')
#         phone_number = request.json.get('phone_number')
#         password = request.json.get('password')
#         confirm_password = request.json.get('confirm_password')

#         # Validate the password
#         if not validate_password(password):
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Password does not meet the requirements.'
#             }), 400

#         # Check if passwords match
#         if password != confirm_password:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Passwords do not match.'
#             }), 400

#         # Check if email or phone number already exists in the main User table
#         user = User.query.filter_by(email=email).first()
#         if user:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Email already exists in the main user database.'
#             }), 400

#         if User.query.filter_by(phone_number=phone_number).first():
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Phone number already exists in the main user database.'
#             }), 400

#         # Generate OTP and set expiry
#         otp = str(random.randint(100000, 999999))
#         otp_expiry = datetime.now() + timedelta(minutes=10)

#         try:
#             # Hash the password
#             hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

#             # Create a new user entry with `is_verified` set to False
#             new_user = User(
#                 username=username,
#                 email=email,
#                 phone_number=phone_number,
#                 password=hashed_password,
#                 otp=otp,
#                 otp_expiry=otp_expiry,
#                 is_verified=False,  # User is not verified yet
#                 registration_date=datetime.now()
#             )

#             db.session.add(new_user)
#             db.session.commit()

#             # Send OTP email
#             send_otp_email(to_email=email, otp=otp)

#             return jsonify({
#                 'status': 'success',
#                 'message': 'User registered successfully! Check your email for the OTP.'
#             }), 201

#         except Exception as e:
#             db.session.rollback()
#             return jsonify({'status': 'error', 'message': str(e)}), 500

#     return jsonify({
#         'status': 'error',
#         'message': 'Method not allowed. Please use POST.'
#     }), 405


ADMIN_KEY = "supersecretadminkey"  # Store securely in env variables

@auth_bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.json.get('username')
        email = request.json.get('email')
        phone_number = request.json.get('phone_number')
        password = request.json.get('password')
        confirm_password = request.json.get('confirm_password')
        admin_key = request.json.get('admin_key', None)  # Optional, defaults to None if not provided

        # Validate the password
        if not validate_password(password):
            return jsonify({
                'status': 'error',
                'message': 'Password does not meet the requirements.'
            }), 400

        # Check if passwords match
        if password != confirm_password:
            return jsonify({
                'status': 'error',
                'message': 'Passwords do not match.'
            }), 400

        # Check if email or phone number already exists
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({
                'status': 'error',
                'message': 'Email already exists in the main user database.'
            }), 400

        if User.query.filter_by(phone_number=phone_number).first():
            return jsonify({
                'status': 'error',
                'message': 'Phone number already exists in the main user database.'
            }), 400

        # Determine the role: 'user' by default, 'admin' if the correct admin_key is provided
        role = 'user'
        if admin_key and admin_key == ADMIN_KEY:
            role = 'admin'

        # Generate OTP and set expiry
        otp = str(random.randint(100000, 999999))
        otp_expiry = datetime.now() + timedelta(minutes=10)

        try:
            # Hash the password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # Create a new user entry
            new_user = User(
                username=username,
                email=email,
                phone_number=phone_number,
                password=hashed_password,
                otp=otp,
                otp_expiry=otp_expiry,
                is_verified=False,  # User is not verified yet
                registration_date=datetime.now(),
                role=role  # Set role as 'admin' or 'user'
            )

            db.session.add(new_user)
            db.session.commit()

            # Send OTP email
            send_otp_email(to_email=email, otp=otp)

            return jsonify({
                'status': 'success',
                'message': 'User registered successfully! Check your email for the OTP.'
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({
        'status': 'error',
        'message': 'Method not allowed. Please use POST.'
    }), 405

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    email = request.json.get('email')

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'User not found.'
        }), 404

    # Check if the OTP has expired
    if user.otp_expiry and datetime.now() < user.otp_expiry:
        return jsonify({
            'status': 'error',
            'message': 'OTP is still valid. Please check your email.'
        }), 400

    # Generate new OTP and set new expiry
    new_otp = str(random.randint(100000, 999999))
    new_otp_expiry = datetime.now() + timedelta(minutes=10)

    try:
        # Update the user's OTP and expiry in the database
        user.otp = new_otp
        user.otp_expiry = new_otp_expiry
        db.session.commit()

        # Send new OTP email
        send_otp_email(to_email=email, otp=new_otp)

        return jsonify({
            'status': 'success',
            'message': 'New OTP has been sent to your email.'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
def validate_password(password):
    """ Validate password strength """
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search("[@#$%^&+=]", password):
        return False
    return True 

@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    email = request.json.get('email')
    otp = request.json.get('otp')

    # Fetch the user by email
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            'status': 'error',
            'message': 'User not found.'
        }), 404

    # Check if OTP is valid
    if user.otp != otp:
        return jsonify({
            'status': 'error',
            'message': 'Invalid OTP.'
        }), 400

    # Check if OTP has expired
    if user.otp_expiry < datetime.now():
        return jsonify({
            'status': 'error',
            'message': 'OTP has expired.'
        }), 400

    # Mark the user as verified
    user.is_verified = True
    user.otp = None
    user.otp_expiry = None
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'User has been successfully verified.'
    }), 200

@auth_bp.route('/verify_email', methods=['POST'])
def verify_email():
    print(f"Request received: {request.json}")
    email = request.json.get('email')
    if check_email_exists(email):
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False}), 404
    


@auth_bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                return jsonify({'status': 'error', 'message': 'Email not verified. Please verify your email.'}), 403
            

            # Generate JWT token
            token = jwt.encode({
                'user_id': user.id,
                'email': user.email,
                'username':user.username,
                'exp': datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            session['username'] = user.username
            session['email'] = email
            return jsonify({
                'status': 'success',
                'message': 'Login successful!',
                'data': {
                    'username': user.username,
                    'email': email,
                    'token': token  # Return the JWT token
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password.'
            }), 401

    return jsonify({
        'status': 'error',
        'message': 'GET method not supported. Please send a POST request.'
    }), 405



def generate_reset_token(email):
    expiration = datetime.utcnow() + timedelta(minutes=30)
    try:
        # Since you're using PyJWT 2.x.x, no need to decode the token.
        token = jwt.encode({'email': email, 'exp': expiration}, current_app.config['SECRET_KEY'], algorithm='HS256')
        # If PyJWT returns a byte string, decode it to a string
        print(f"Generated token: {token}")
        return token
    except Exception as e:
        print(f"Error encoding token: {e}")
        return None


def verify_reset_token(token):
    print(f"Received token for verification: {token}")
    try:
        # Decode the token using the secret key and HS256 algorithm
        data = jwt.decode(token, current_app.config[SECRET_KEY], algorithms=['HS256'])
        print(f"Decoded token data: {data}")
        return data['email']
    except jwt.ExpiredSignatureError:
        # Handle case where the token has expired
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        # Handle case where the token is invalid
        print("Invalid token.")
        return None
    except Exception as e:
        # Handle any other exceptions that may occur
        print(f"Unexpected error: {e}")
        return None
    
# def get_db_connection():
#     try:
#         print("Attempting to connect to the database...")
#         conn = pymysql.connect(
#             host='13.234.113.49',
#             user='admin',
#             password='Admin#235',
#             db='turtu_website'
#         )
#         print("Successfully connected to the database!")
#         return conn
#     except pymysql.MySQLError as e:
#         print(f"Database connection error: {e}")
#         return None

    
@auth_bp.route('/request_password_reset', methods=['POST'])
def request_password_reset():
    email = request.form.get('email', '').strip()
    
    if not email:
        return jsonify({'status': 'error', 'message': 'Please provide an email address.'}), 400
    
    conn = None
    try:
        print(f"Email received for password reset: {email}")  # Debugging
        conn = get_db_connection()
        if conn is None:
            print("Database connection failed!")  # Debugging
            return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        print(f"User fetched: {user}")  # Debugging

        if user:
            token = generate_reset_token(email)
            print(f"request_reset_password token: {token}")  # Debugging
            if token:
                # Store the token in the database
                expiration = datetime.utcnow() + timedelta(minutes=30)
                cursor.execute("INSERT INTO password_reset_tokens (email, token, expiration) VALUES (%s, %s, %s)",
                               (email, token, expiration))
                conn.commit()
                # Construct the reset link using a domain name
                base_url = os.getenv("ALLOWED_ORIGINS2")  # Define BASE_URL in your .env file
                reset_link = f"{base_url}/reset-password/{token}"
                
                send_password_reset_email(email, reset_link)
                return jsonify({'status': 'success', 'message': 'A password reset link has been sent to your email.'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Failed to generate reset token.'}), 500
        else:
            return jsonify({'status': 'error', 'message': 'Email not found.'}), 404

    except Exception as e:
        print(f'An error occurred: {e}')  # Print to server logs
        return jsonify({'status': 'error', 'message': f'An error occurred: {e}'}), 500

    finally:
        if conn:
            conn.close()


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = None
    try:
        if request.method == 'POST':
            # Retrieve the new password from the form data
            data = request.get_json()
            new_password = data.get('password')
            confirm_password = data.get('confirm_password')
            print(f"Received password: {new_password}")
            print(f"Received confirm_password: {confirm_password}") 


            # Ensure both password fields are provided
            if not new_password or not confirm_password:
                return jsonify({"message": "Both password fields are required."}), 400

            # Ensure passwords match
            if new_password != confirm_password:
                return jsonify({"message": "Passwords do not match."}), 400

            # Verify the token
            email = verify_reset_token(token)
            if email is None:
                return jsonify({"message": "Invalid or expired token."}), 400

            # Hash the new password
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

            # Update the password in the database
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            conn.commit()

            # Optionally, delete the token from the database (if you're storing tokens)
            cursor.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
            conn.commit()

            return jsonify({"message": "Password has been updated successfully!"}), 200

        else:
            # For the GET request, return token information or render a template
            return jsonify({"token": token}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()


@auth_bp.route('/test_post', methods=['GET', 'POST'])
def test_post():
    return "POST request received", 200
