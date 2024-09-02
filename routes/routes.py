from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app as app, jsonify
import mysql.connector
from mysql.connector import IntegrityError
from db.db import get_db_connection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
import re
import random
import string
import pymysql
from datetime import datetime, timedelta
from datetime import datetime
import pytz
from config.config import Config
from mysql.connector import Error
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import logging
import jwt
from models.models import db, User, CareerApplication, Contact
from functools import wraps

routes_bp = Blueprint('routes', __name__)

# Define the timezone
tz = pytz.timezone('UTC')  # Or your local time zone

def send_confirmation_email(to_email, username):
    with app.app_context():
        body = render_template('confirmation_email.html', username=username)
    
    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'html'))
    msg['Subject'] = 'Welcome to Turtu!'
    msg['From'] = Config.SMTP_USERNAME
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)
        print("Confirmation email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

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

@routes_bp.route('/')
def home():
    return render_template('home.html')


# @routes_bp.route('/register', methods=['POST'])
# def register():
#     if request.method == 'POST':
#         username = request.json.get('username')
#         email = request.json.get('email')
#         password = request.json.get('password')

#         # Validate the password (ensure validate_password is defined)
#         if not validate_password(password):
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Password does not meet the requirements.'
#             }), 400

#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

#         try:
#             user = User(username=username, email=email, password=hashed_password)
#             db.session.add(user)
#             db.session.commit()
#             session['username'] = username
#             return jsonify({
#                 'status': 'success',
#                 'message': 'Registration successful! You can now log in.'
#             }), 201
#         except IntegrityError:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Email already in use. Please use a different email.'
#             }), 400
#         except Exception as e:
#             print(f"Database error: {e}")
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Registration failed due to a database error.'
#             }), 500
#         finally:
#             db.session.rollback()

@routes_bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.json.get('username')
        email = request.json.get('email')
        password = request.json.get('password')

        # Validate the password (ensure validate_password is defined)
        if not validate_password(password):
            return jsonify({
                'status': 'error',
                'message': 'Password does not meet the requirements.'
            }), 400

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({
                'status': 'error',
                'message': 'Email already exists.'
            }), 400

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create and save the new user
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'User registered successfully!'}), 201

    return jsonify({
        'status': 'error',
        'message': 'Method not allowed. Please use POST.'
    }), 405

#new code 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            # Return a JSON response with a 401 status code if not logged in
            return jsonify({'error': 'Unauthorized access. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function

@routes_bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            session['email'] = email
            return jsonify({
                'status': 'success',
                'message': 'Login successful!',
                'data': {
                    'username': user.username,
                    'email': email
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

@routes_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    response = jsonify({'message': 'Logged out successfully.', 'status': 'success'})
    response.set_cookie('session', '', expires=0)  # Clear the cookie
    return response

@routes_bp.route('/career', methods=['POST'])
@login_required
def career():
    if request.method == 'POST':
        # Retrieve form data
        email = request.form.get('email')
        phone_number = request.form.get('phoneNumber')  # Ensure this matches the key used in Postman
        profile = request.form.get('profile')
        resume = request.files.get('resume')

        # Debug print statements
        print(f"Email: {email}")
        print(f"Phone Number: {phone_number}")
        print(f"Profile: {profile}")
        print(f"Resume: {resume}")

        # Check if all fields are provided
        if not email or not phone_number or not profile or not resume:
            return jsonify({
                'status': 'error',
                'message': 'All fields are required.'
            }), 400

        # Save resume file if it is valid
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume_filename = os.path.join('uploads', filename)
            resume.save(resume_filename)
        else:
            resume_filename = ''

        try:
            # Create a new career application entry
            application = CareerApplication(
                email=email,
                phone_number=phone_number,
                profile=profile,
                resume_filename=resume_filename  # Ensure this matches the model
            )
            db.session.add(application)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Application submitted successfully!',
                'data': {
                    'email': email,
                    'phone_number': phone_number,
                    'profile': profile,
                    'resume_filename': resume_filename
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'An error occurred: {e}'
            }), 500



# @routes_bp.route('/show-career-submission')
# def show_career_submission():
#     if 'career_email' not in session:
#         return redirect(url_for('routes.career'))

#     user_info = {
#         'email': session.get('career_email'),
#         'phone_number': session.get('career_phone_number'),
#         'profile': session.get('career_profile'),
#         'resume_filename': session.get('career_resume_filename')
#     }

#     return render_template('show_career_submission.html', user_info=user_info)

@routes_bp.route('/contact', methods=['POST'])
@login_required
def contact():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        queries = request.form.get('queries')

        try:
            contact = Contact(username=username, email=email, phone_number=phone_number, queries=queries)
            db.session.add(contact)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Your message has been sent!',
                'data': {
                    'username': username,
                    'email': email,
                    'phone_number': phone_number,
                    'queries': queries
                }
            }), 201
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'An error occurred: {e}'
            }), 500
        finally:
            db.session.rollback()

    return jsonify({
        'status': 'error',
        'message': 'GET method not supported. Please send a POST request.'
    }), 405

# @routes_bp.route('/show-submission')
# def show_submission():
#     if 'username' not in session:
#         return redirect(url_for('routes.contact'))

#     user_info = {
#         'username': session.get('username'),
#         'email': session.get('email'),
#         'phone_number': session.get('phone_number'),
#         'queries': session.get('queries')
#     }
    
#     return render_template('show_submission.html', user_info=user_info)

# @routes_bp.route('/dashboard')
# def dashboard():
#     if 'email' in session:
#         return render_template('dashboard.html')
#     else:
#         return redirect(url_for('routes.login'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}

#===============================================

# Define the secret key for encoding/decoding tokens (you should ideally keep this in your config)
SECRET_KEY = 'SECRET_KEY'

def generate_reset_token(email):
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({'email': email, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    return token

def verify_reset_token(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return data['email']
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# @routes_bp.route('/request_password_reset', methods=['GET', 'POST'])
# def request_password_reset():
#     print(f"Request method: {request.method}")  # Debugging statement
#     if request.method == 'POST':
#         email = request.form.get('email', '').strip()
#         print(f"Form data: {request.form}")
#         if email:  # Proceed only if email is entered
#             try:
#                 conn = get_db_connection()
#                 cursor = conn.cursor()

#                 cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
#                 user = cursor.fetchone()

#                 if user:
#                     token = generate_reset_token(email)
#                     reset_link = url_for('routes.reset_password', token=token, _external=True)

#                     send_password_reset_email(email, reset_link)
#                     flash('A password reset link has been sent to your email.', 'info')
#                 else:
#                     flash('Email not found.', 'error')

#             except Exception as e:
#                 flash(f'An error occurred: {e}', 'danger')

#             finally:
#                 conn.close()
#         else:
#             flash('Please provide an email address.', 'error')

#             # Redirect to a new route to prevent form resubmission
#         return redirect(url_for('routes.request_password_reset_result'))

#     # Rendering the template for both GET and POST methods
#     return render_template('request_password_reset.html')


# from sqlalchemy import create_engine
# def get_db_connection():
#     try:
#         print("Attempting to connect to the database...")
#         conn = pymysql.connect(
#             host='localhost',
#             user='root',
#             password='*Sneha1310@1310',
#             db='user_db'
#         )
#         print("Successfully connected to the database!")
#         return conn
#     except pymysql.MySQLError as e:
#         print(f"Database connection error: {e}")
#         return None



    
# @routes_bp.route('/request_password_reset', methods=['POST'])
# def request_password_reset():
#     if request.method == 'POST':
#         email = request.form.get('email', '').strip()
#         if email:
#             try:
#                 print("Getting database connection...")  # Debugging
#                 conn = get_db_connection()
#                 if conn is None:
#                     print("Database connection failed!")  # Debugging
#                     return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

#                 cursor = conn.cursor()
#                 cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
#                 user = cursor.fetchone()

#                 if user:
#                     token = generate_reset_token(email)
#                     # reset_link = url_for('routes.reset_password', token=token, _external=True)
#                     send_password_reset_email(email, token)
#                     flash('A password reset link has been sent to your email.', 'info')
#                 else:
#                     flash('Email not found.', 'error')

#             except Exception as e:
#                 print(f'An error occurred: {e}')  # Print to server logs
#                 flash(f'An error occurred: {e}', 'danger')
#                 return redirect(url_for('routes.request_password_reset'))

#             finally:
#                 if conn:
#                     conn.close()
#         else:
#             flash('Please provide an email address.', 'error')
#             return redirect(url_for('routes.request_password_reset'))

#     return render_template('request_password_reset.html')

@routes_bp.route('/request_password_reset', methods=['POST'])
def request_password_reset():
    email = request.form.get('email', '').strip()
    
    if not email:
        return jsonify({'status': 'error', 'message': 'Please provide an email address.'}), 400
    
    try:
        print("Getting database connection...")  # Debugging
        conn = get_db_connection()
        if conn is None:
            print("Database connection failed!")  # Debugging
            return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            token = generate_reset_token(email)
            send_password_reset_email(email, token)
            return jsonify({'status': 'success', 'message': 'A password reset link has been sent to your email.'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Email not found.'}), 404

    except Exception as e:
        print(f'An error occurred: {e}')  # Print to server logs
        return jsonify({'status': 'error', 'message': f'An error occurred: {e}'}), 500

    finally:
        if conn:
            conn.close()

        return jsonify({'status': 'error', 'message': 'Unexpected error occurred.'}), 500

# @routes_bp.route('/request_password_reset_result')
# def request_password_reset_result():
#     # Display the result after redirection
#     return render_template('request_password_reset_result.html')


# def send_password_reset_email(to_email, reset_link):
#     body = f"""
#     <p>You have requested a password reset. Click the link below to reset your password:</p>
#     <p><a href="{reset_link}">Reset Password</a></p>
#     """
#     msg = MIMEMultipart()
#     msg.attach(MIMEText(body, 'html'))
#     msg['Subject'] = 'Password Reset Request'
#     msg['From'] = Config.SMTP_USERNAME
#     msg['To'] = to_email

#      # Print email details for debugging
#     print("Sending email...")
#     print(f"Subject: {msg['Subject']}")
#     print(f"From: {msg['From']}")
#     print(f"To: {msg['To']}")
#     print(f"Body: {body}")

#     try:
#         server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
#         server.starttls()
#         server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
#         server.send_message(msg)
#         print("Password reset email sent successfully!")
#     except Exception as e:
#         print(f"Failed to send password reset email: {e}")
#     finally:
#         server.quit()
        
def send_password_reset_email(to_email, token):
    reset_link = f"http://127.0.0.1:5000/reset_password/{token}"
    body = f"""
    <p>You have requested a password reset. Use the following token to reset your password:</p>
    <p><strong>Token: {token}</strong></p>
    <p>Alternatively, you can use the following link:</p>
    <p><a href="{reset_link}">Reset Password</a></p>
    """
    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'html'))
    msg['Subject'] = 'Password Reset Request'
    msg['From'] = Config.SMTP_USERNAME
    msg['To'] = to_email

    # Print email details for debugging
    print("Sending email...")
    print(f"Subject: {msg['Subject']}")
    print(f"From: {msg['From']}")
    print(f"To: {msg['To']}")
    print(f"Body: {body}")

    try:
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)
        print("Password reset email sent successfully!")
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
    finally:
        server.quit()



# @routes_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     if request.method == 'POST':
#         # Retrieve the new password from the form data
#         new_password = request.form.get('password')
#         email = verify_reset_token(token)

#         if email is None:
#             return "Invalid or expired token.", 400

#         # Ensure new_password is not None or empty
#         if not new_password:
#             return "Password is required.", 400

#         # Hash the new password
#         hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

#         try:
#             conn = get_db_connection()
#             cursor = conn.cursor()
#             cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
#             conn.commit()
#             return "Password has been updated successfully!", 200
#         except Exception as e:
#             return f"An error occurred: {e}", 500
#         finally:
#             conn.close()
#     else:
#         # Render the password reset form (GET request)
#         return render_template('reset_password.html', token=token)
@routes_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        # Retrieve the new password from the form data
        new_password = request.form.get('password')
        email = verify_reset_token(token)

        if email is None:
            return {"message": "Invalid or expired token."}, 400

        # Ensure new_password is not None or empty
        if not new_password:
            return {"message": "Password is required."}, 400

        # Hash the new password
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            conn.commit()
            return {"message": "Password has been updated successfully!"}, 200
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            conn.close()
    else:
        # For the GET request, just return a simple JSON message (or debug information)
        return {"token": token}, 200


@routes_bp.route('/test_post', methods=['POST'])
def test_post():
    return "POST request received", 200
