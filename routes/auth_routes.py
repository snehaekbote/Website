from flask import Blueprint, request, jsonify
from models.models import db
from werkzeug.security import generate_password_hash
from db.db import get_db_connection
from datetime import datetime, timedelta
from datetime import datetime
import pymysql
import jwt

auth_bp = Blueprint('auth', __name__)

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




@auth_bp.route('/request_password_reset', methods=['POST'])
def request_password_reset():
    email = request.form.get('email', '').strip()
    
    if not email:
        return jsonify({'status': 'error', 'message': 'Please provide an email address.'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            token = generate_reset_token(email)
            if token:
                send_password_reset_email(email, token)
                return jsonify({'status': 'success', 'message': 'A password reset link has been sent to your email.'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Failed to generate reset token.'}), 500
        else:
            return jsonify({'status': 'error', 'message': 'Email not found.'}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'An error occurred: {e}'}), 500

    finally:
        if conn:
            conn.close()


@auth_bp.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = verify_reset_token(token)

        if email is None:
            return jsonify({"message": "Invalid or expired token."}), 400

        if not new_password or not confirm_password:
            return jsonify({"message": "Both password fields are required."}), 400

        if new_password != confirm_password:
            return jsonify({"message": "Passwords do not match."}), 400
        
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            conn.commit()
            return jsonify({"message": "Password has been updated successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()
    else:
        return jsonify({"token": token}), 200
