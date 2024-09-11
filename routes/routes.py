from flask import Blueprint, render_template, request, session,current_app as app, jsonify, send_file
import mysql.connector
from mysql.connector import IntegrityError
from db.db import get_db_connection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
import re
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
import random
import jwt
from models.models import db, User, CareerApplication, Contact, check_email_exists
from functools import wraps
from flask_cors import CORS
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from apscheduler.schedulers.background import BackgroundScheduler

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


def create_engine_from_config():
    try:
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        print("Successfully connected to the database")
        return engine
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to export multiple tables to an Excel file
def export_multiple_tables_to_excel(engine, tables, output_file):
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for table_name in tables:
                query = f"SELECT * FROM {table_name}"
                data_frame = pd.read_sql(query, engine)
                data_frame.to_excel(writer, sheet_name=table_name, index=False)
        print(f"Data from all tables successfully exported to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error exporting data: {e}")
        return None


# Route to export data on-demand
@routes_bp.route('/export-data', methods=['GET'])
def export_data_route():
    try:
        # Create SQLAlchemy engine
        engine = create_engine_from_config()
        if engine is None:
            return jsonify({'error': 'Failed to connect to the database'}), 500

        # Define tables to export
        tables = ["career_applications", "contacts", "users"]  # Replace with actual table names
        excel_file = "api_export3.xlsx"

        # Export the data
        file_path = export_multiple_tables_to_excel(engine, tables, excel_file)
        if file_path:
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "Failed to export data"}), 500

    except Exception as e:
        return jsonify({'error': str(e)})

# Function to send OTP email (you need to implement this)
def send_otp_email(to_email, otp):
    body = f"""
    <p>Your OTP for login is: <strong>{otp}</strong></p>
    <p>If you did not request this, please ignore this email.</p>
    """
    msg = MIMEText(body, 'html')
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = app.config['SMTP_USERNAME']
    msg['To'] = to_email

    try:
        # Connect to SMTP server
        server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
        server.starttls()
        server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
        
        # Send the email
        server.send_message(msg)
        logging.info(f"OTP email sent successfully to {to_email}")
        return True
    
    except smtplib.SMTPException as e:
        # Log the error
        logging.error(f"Failed to send OTP email to {to_email}: {e}")
        return False
    
    finally:
        if server:
            server.quit()

#2nd version
@routes_bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.json.get('username')
        email = request.json.get('email')
        phone_number = request.json.get('phone_number')
        password = request.json.get('password')
        confirm_password = request.json.get('confirm_password')

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

        # Check if email or phone number already exists in the main User table
        if User.query.filter_by(email=email).first():
            return jsonify({
                'status': 'error',
                'message': 'Email already exists in the main user database.'
            }), 400

        if User.query.filter_by(phone_number=phone_number).first():
            return jsonify({
                'status': 'error',
                'message': 'Phone number already exists in the main user database.'
            }), 400

        # Check if the user is already in the temp_users table
        sql = text("SELECT * FROM temp_users WHERE email = :email")
        temp_user = db.session.execute(sql, {'email': email}).fetchone()

        # Generate OTP and set expiry
        otp = str(random.randint(100000, 999999))
        otp_expiry = datetime.now() + timedelta(minutes=10)


        

        try:
            if temp_user:
                # User exists in temp_users, update the OTP and expiry
                sql = text(
                    "UPDATE temp_users SET otp = :otp, otp_expiry = :otp_expiry, registration_date = :registration_date "
                    "WHERE email = :email"
                )
                db.session.execute(sql, {
                    'otp': otp,
                    'otp_expiry': otp_expiry,
                    'registration_date': datetime.now(),
                    'email': email
                })
            else:
                
                # Insert new record into temp_users
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                sql = text(
                    "INSERT INTO temp_users (username, email, phone_number, password, otp, otp_expiry, registration_date) "
                    "VALUES (:username, :email, :phone_number, :password, :otp, :otp_expiry, :registration_date)"
                )
                db.session.execute(sql, {
                    'username': username,
                    'email': email,
                    'phone_number': phone_number,
                    'password': hashed_password,
                    'otp': otp,
                    'otp_expiry': otp_expiry,
                    'registration_date': datetime.now()
                })
            
            # Commit the transaction
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


@routes_bp.route('/verify_email', methods=['POST'])
def verify_email():
    print(f"Request received: {request.json}")
    email = request.json.get('email')
    if check_email_exists(email):
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False}), 404

# OTP Verification route
# @routes_bp.route('/verify_otp', methods=['POST'])
# def verify_otp():
#     if request.method == 'POST':
#         email = request.json.get('email')
#         otp = request.json.get('otp')

#         user = User.query.filter_by(email=email).first()
#         if user and user.otp == otp and user.otp_expiry > datetime.now():
#             user.email_verified = True
#             db.session.commit()
#             return jsonify({'status': 'success', 'message': 'Email verified successfully! You can now log in.'}), 200
#         else:
#             return jsonify({'status': 'error', 'message': 'Invalid or expired OTP.'}), 400

#     return jsonify({
#         'status': 'error',
#         'message': 'Method not allowed. Please use POST.'
#     }), 405


@routes_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    if request.method == 'POST':
        email = request.json.get('email')
        otp = request.json.get('otp')

        # Retrieve registration data from temporary storage
        sql = text("SELECT * FROM temp_users WHERE email = :email")
        result = db.session.execute(sql, {'email': email}).fetchone()

        if result:
            # Access columns by index
            temp_user = {
                'username': result[1],  # Adjust index based on column order
                'email': result[2],     # Adjust index based on column order
                'phone_number': result[3],  # Adjust index based on column order
                'password': result[4],  # Adjust index based on column order
                'otp': result[5],       # Adjust index based on column order
                'otp_expiry': result[6]  # Adjust index based on column order
            }

            if temp_user['otp'] == otp and temp_user['otp_expiry'] > datetime.now():
                # Create and save the new user in the main database
                try:
                    new_user = User(
                        username=temp_user['username'],
                        email=email,
                        phone_number=temp_user['phone_number'],
                        password=temp_user['password'],
                        email_verified=True
                    )
                    db.session.add(new_user)
                    db.session.commit()

                    # Remove from temporary storage
                    delete_sql = text("DELETE FROM temp_users WHERE email = :email")
                    db.session.execute(delete_sql, {'email': email})
                    db.session.commit()

                    return jsonify({'status': 'success', 'message': 'Email verified successfully! You can now log in.'}), 200
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'status': 'error', 'message': str(e)}), 500
            else:
                return jsonify({'status': 'error', 'message': 'Invalid or expired OTP.'}), 400
        else:
            return jsonify({'status': 'error', 'message': 'No user found with this email.'}), 404

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

# @routes_bp.route('/login', methods=['POST'])
# def login():
#     if request.method == 'POST':
#         email = request.json.get('email')
#         password = request.json.get('password')

#         user = User.query.filter_by(email=email).first()

#         if user and check_password_hash(user.password, password):
#             session['username'] = user.username
#             session['email'] = email
#             return jsonify({
#                 'status': 'success',
#                 'message': 'Login successful!',
#                 'data': {
#                     'username': user.username,
#                     'email': email
#                 }
#             }), 200
#         else:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Invalid email or password.'
#             }), 401

#     return jsonify({
#         'status': 'error',
#         'message': 'GET method not supported. Please send a POST request.'
#     }), 405

# Login route
@routes_bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.email_verified:
                return jsonify({'status': 'error', 'message': 'Email not verified. Please verify your email.'}), 403
            
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



@routes_bp.route('/contact', methods=['POST'])
@login_required
def contact():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        queries = request.form.get('queries')

        # Check if the user is registered
        if not check_email_exists(email):
            return jsonify({
                'status': 'error',
                'message': 'User not registered. Please sign up first.'
            }), 404
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



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}

#===============================================

# Define the secret key for encoding/decoding tokens (you should ideally keep this in your config)
SECRET_KEY = 'SECRET_KEY'

def generate_reset_token(email):
    expiration = datetime.utcnow() + timedelta(hours=1)
    try:
        # Since you're using PyJWT 2.x.x, no need to decode the token.
        token = jwt.encode({'email': email, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
        # If PyJWT returns a byte string, decode it to a string
        print(f"Generated token: {token}")
        return token
    except Exception as e:
        print(f"Error encoding token: {e}")
        return None
    
    # Test the function
print(generate_reset_token('snehaekbote13@gmail.com'))

def verify_reset_token(token):
    print(f"Received token for verification: {token}")
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print(f"Decoded token data: {data}")
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



from sqlalchemy import create_engine
def get_db_connection():
    try:
        print("Attempting to connect to the database...")
        conn = pymysql.connect(
            host='13.234.113.49',
            user='admin',
            password='Admin#235',
            db='turtu_website'
        )
        print("Successfully connected to the database!")
        return conn
    except pymysql.MySQLError as e:
        print(f"Database connection error: {e}")
        return None



@routes_bp.route('/request_password_reset', methods=['POST'])
def request_password_reset():
    email = request.form.get('email', '').strip()
    
    if not email:
        return jsonify({'status': 'error', 'message': 'Please provide an email address.'}), 400
    
    conn = None
    try:
        print("Getting database connection...")  # Debugging
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
                send_password_reset_email(email, token)
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


        
def send_password_reset_email(to_email, token):
    try:
        print("Entering send_password_reset_email function...")  # Debugging
        reset_link = f"http://13.235.115.160:5000/reset_password/{token}"
        print(f"Reset link: {reset_link}")  # Debugging

        body = f"""
        <p>You have requested a password reset. Use the following token to reset your password:</p>
        <p><strong>Token: {token}</strong></p>
        <p>Alternatively, you can use the following link:</p>
        <p><a href="{reset_link}">Reset Password</a></p>
        """
        print(f"Sending token: {token}")
    except Exception as e:
        print(f"Error in sending email: {e}")  # Log the exception
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



@routes_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        # Retrieve the new password from the form data
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = verify_reset_token(token)

        if email is None:
            return {"message": "Invalid or expired token."}, 400

        # Ensure new_password and confirm_password are not None or empty
        if not new_password or not confirm_password:
            return jsonify({"message": "Both password fields are required."}), 400

        # Check if new_password and confirm_password match
        if new_password != confirm_password:
            return jsonify({"message": "Passwords do not match."}), 400
        
        
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

@routes_bp.route('/test_pos', methods=['POST'])
def test_route():
    return "POST request received", 200
