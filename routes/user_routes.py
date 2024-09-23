<<<<<<< Updated upstream
from flask import current_app, Blueprint, g, request, jsonify
import os
from werkzeug.utils import secure_filename
from utils.email_utils import send_career_email, send_query_contact_email
from models.models import db, CareerApplication, Contact
import jwt
from functools import wraps

user_bp = Blueprint('user', __name__)

# Utility function to extract and decode JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Bearer <token>

        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token is missing!'
            }), 401

        try:
            # Decode the token to get user info
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user = data  # Store user data in g for access in the route
        except jwt.ExpiredSignatureError:
            return jsonify({
                'status': 'error',
                'message': 'Token has expired. Please log in again.'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid token. Please log in again.'
            }), 401

        return f(*args, **kwargs)
    return decorated
@user_bp.route('/career', methods=['POST'])
@token_required  # Apply the token_required decorator to require JWT
def career():
    if request.method == 'POST':
        # Retrieve form data
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        profile = request.form.get('profile')
        resume = request.files.get('resume')

        # Check if all required fields are provided
        if not email or not phone_number or not profile or not resume:
            return jsonify({
                'status': 'error',
                'message': 'All fields are required.'
            }), 400

        # Validate and save the resume file
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume_filename = os.path.join('uploads', filename)
            resume.save(resume_filename)
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid file format for resume.'
            }), 400

        try:
            # Fetch the current user's ID from the decoded JWT token
            user_id = g.user['user_id']

            if not user_id:
                return jsonify({
                    'status': 'error',
                    'message': 'User is not logged in.'
                }), 403

            # Create a new career application entry with the user_id
            application = CareerApplication(
                user_id=user_id,
                email=email,
                phone_number=phone_number,
                profile=profile,
                resume_filename=resume_filename
            )
            db.session.add(application)
            db.session.commit()

            # Fetch the application_id after commit
            application_id = application.id

            # Optional: Send a confirmation email after saving the application
            send_career_email(
                to_email=email,
                username=g.user['username'],  # Extract username from the JWT
                profile=profile,
                resume_filename=resume_filename,
                application_id=application_id
            )

            return jsonify({
                'status': 'success',
                'message': 'Application submitted successfully!',
                'data': {
                    'user_id': user_id,
                    'email': email,
                    'phone_number': phone_number,
                    'profile': profile,
                    'resume_filename': resume_filename,
                    'application_id': application_id
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'An error occurred: {e}'
            }), 500

    return jsonify({
        'status': 'error',
        'message': 'GET method not supported. Please send a POST request.'
    }), 405

# @user_bp.route('/career', methods=['POST'])
# def career():
#     if request.method == 'POST':
#         # Retrieve form data
#         email = request.form.get('email')
#         phone_number = request.form.get('phone_number')
#         profile = request.form.get('profile')
#         resume = request.files.get('resume')

#         # Check if all required fields are provided
#         if not email or not phone_number or not profile or not resume:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'All fields are required.'
#             }), 400

#         # Validate and save the resume file
#         if resume and allowed_file(resume.filename):
#             filename = secure_filename(resume.filename)
#             resume_filename = os.path.join('uploads', filename)
#             resume.save(resume_filename)
#         else:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Invalid file format for resume.'
#             }), 400

#         try:
#             # Fetch the current user's ID from session or g.user (assuming user is logged in)
#             user_id = g.user.id if g.user else None  # Adjust based on your session management

#             if not user_id:
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'User is not logged in.'
#                 }), 403

#             # Create a new career application entry with the user_id
#             application = CareerApplication(
#                 user_id=user_id,
#                 email=email,
#                 phone_number=phone_number,
#                 profile=profile,
#                 resume_filename=resume_filename
#             )
#             db.session.add(application)
#             db.session.commit()

#             # Fetch the application_id after commit
#             application_id = application.id


#             # Optional: Send a confirmation email after saving the application
#             send_career_email(
#                 to_email=email, 
#                 username=g.user.username,  # Assuming username is stored in g.user
#                 profile=profile, 
#                 resume_filename=resume_filename,
#                 application_id=application_id
#             )

#             return jsonify({
#                 'status': 'success',
#                 'message': 'Application submitted successfully!',
#                 'data': {
#                     'user_id': user_id,
#                     'email': email,
#                     'phone_number': phone_number,
#                     'profile': profile,
#                     'resume_filename': resume_filename,
#                     'application_id': application_id
#                 }
#             }), 201
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({
#                 'status': 'error',
#                 'message': f'An error occurred: {e}'
#             }), 500

#     return jsonify({
#         'status': 'error',
#         'message': 'GET method not supported. Please send a POST request.'
#     }), 405


@user_bp.route('/contact', methods=['POST'])
def contact(user_id, username):
    print("User ID from token:", user_id)  # Debugging statement
    print("Username from token:", username)  # Debugging statement

    if request.method == 'POST':
        # Retrieve form data (queries and phone number)
        username = request.json.get('username')
        email = request.json.get('email')
        phone_number = request.json.get('phone_number')
        queries = request.json.get('queries')

        if not email or not phone_number or not queries:
            return jsonify({
                'status': 'error',
                'message': 'All fields are required.'
            }), 400

        try:
            # Create a new contact entry with the form-provided values
            contact = Contact(
                username=username,
                email=email,
                phone_number=phone_number,
                queries=queries,
                user_id=user_id  # User ID from token
            )
            db.session.add(contact)
            db.session.commit()

            # Send confirmation email
            send_query_contact_email(
                to_email=email,
                username=username,
                query_details=queries
            )

            return jsonify({
                'status': 'success',
                'message': 'Your message has been sent! A confirmation email has been sent to you.',
                'data': {
                    'username':username,
                    'email': email,
                    'phone_number': phone_number,
                    'queries': queries,
                    'user_id': user_id
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            print("Error during contact creation:", e)  # Debugging statement
            return jsonify({
                'status': 'error',
                'message': f'An error occurred: {e}'
            }), 500

    return jsonify({
        'status': 'error',
        'message': 'GET method not supported. Please send a POST request.'
    }), 405


def allowed_file(filename):
=======
from flask import current_app, Blueprint, g, request, jsonify
import os
from werkzeug.utils import secure_filename
from routes.auth_routes import login_required
from utils.email_utils import send_career_email, send_query_contact_email
from models.models import db, CareerApplication, Contact
import jwt
from functools import wraps

user_bp = Blueprint('user', __name__)

# Utility function to extract and decode JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Bearer <token>

        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token is missing!'
            }), 401

        try:
            # Decode the token to get user info
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user = data  # Store user data in g for access in the route
        except jwt.ExpiredSignatureError:
            return jsonify({
                'status': 'error',
                'message': 'Token has expired. Please log in again.'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid token. Please log in again.'
            }), 401

        return f(*args, **kwargs)
    return decorated
@user_bp.route('/career', methods=['POST'])
@token_required  # Apply the token_required decorator to require JWT
def career():
    if request.method == 'POST':
        # Retrieve form data
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        profile = request.form.get('profile')
        resume = request.files.get('resume')

        # Check if all required fields are provided
        if not email or not phone_number or not profile or not resume:
            return jsonify({
                'status': 'error',
                'message': 'All fields are required.'
            }), 400

        # Validate and save the resume file
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume_filename = os.path.join('uploads', filename)
            resume.save(resume_filename)
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid file format for resume.'
            }), 400

        try:
            # Fetch the current user's ID from the decoded JWT token
            user_id = g.user['user_id']

            if not user_id:
                return jsonify({
                    'status': 'error',
                    'message': 'User is not logged in.'
                }), 403

            # Create a new career application entry with the user_id
            application = CareerApplication(
                user_id=user_id,
                email=email,
                phone_number=phone_number,
                profile=profile,
                resume_filename=resume_filename
            )
            db.session.add(application)
            db.session.commit()

            # Fetch the application_id after commit
            application_id = application.id

            # Optional: Send a confirmation email after saving the application
            send_career_email(
                to_email=email,
                username=g.user['username'],  # Extract username from the JWT
                profile=profile,
                resume_filename=resume_filename,
                application_id=application_id
            )

            return jsonify({
                'status': 'success',
                'message': 'Application submitted successfully!',
                'data': {
                    'user_id': user_id,
                    'email': email,
                    'phone_number': phone_number,
                    'profile': profile,
                    'resume_filename': resume_filename,
                    'application_id': application_id
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'An error occurred: {e}'
            }), 500

    return jsonify({
        'status': 'error',
        'message': 'GET method not supported. Please send a POST request.'
    }), 405

# @user_bp.route('/career', methods=['POST'])
# def career():
#     if request.method == 'POST':
#         # Retrieve form data
#         email = request.form.get('email')
#         phone_number = request.form.get('phone_number')
#         profile = request.form.get('profile')
#         resume = request.files.get('resume')

#         # Check if all required fields are provided
#         if not email or not phone_number or not profile or not resume:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'All fields are required.'
#             }), 400

#         # Validate and save the resume file
#         if resume and allowed_file(resume.filename):
#             filename = secure_filename(resume.filename)
#             resume_filename = os.path.join('uploads', filename)
#             resume.save(resume_filename)
#         else:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Invalid file format for resume.'
#             }), 400

#         try:
#             # Fetch the current user's ID from session or g.user (assuming user is logged in)
#             user_id = g.user.id if g.user else None  # Adjust based on your session management

#             if not user_id:
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'User is not logged in.'
#                 }), 403

#             # Create a new career application entry with the user_id
#             application = CareerApplication(
#                 user_id=user_id,
#                 email=email,
#                 phone_number=phone_number,
#                 profile=profile,
#                 resume_filename=resume_filename
#             )
#             db.session.add(application)
#             db.session.commit()

#             # Fetch the application_id after commit
#             application_id = application.id


#             # Optional: Send a confirmation email after saving the application
#             send_career_email(
#                 to_email=email, 
#                 username=g.user.username,  # Assuming username is stored in g.user
#                 profile=profile, 
#                 resume_filename=resume_filename,
#                 application_id=application_id
#             )

#             return jsonify({
#                 'status': 'success',
#                 'message': 'Application submitted successfully!',
#                 'data': {
#                     'user_id': user_id,
#                     'email': email,
#                     'phone_number': phone_number,
#                     'profile': profile,
#                     'resume_filename': resume_filename,
#                     'application_id': application_id
#                 }
#             }), 201
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({
#                 'status': 'error',
#                 'message': f'An error occurred: {e}'
#             }), 500

#     return jsonify({
#         'status': 'error',
#         'message': 'GET method not supported. Please send a POST request.'
#     }), 405


@user_bp.route('/contact', methods=['POST'])
def contact(user_id, username):
    print("User ID from token:", user_id)  # Debugging statement
    print("Username from token:", username)  # Debugging statement

    if request.method == 'POST':
        # Retrieve form data (queries and phone number)
        username = request.json.get('username')
        email = request.json.get('email')
        phone_number = request.json.get('phone_number')
        queries = request.json.get('queries')

        if not email or not phone_number or not queries:
            return jsonify({
                'status': 'error',
                'message': 'All fields are required.'
            }), 400

        try:
            # Create a new contact entry with the form-provided values
            contact = Contact(
                username=username,
                email=email,
                phone_number=phone_number,
                queries=queries,
                user_id=user_id  # User ID from token
            )
            db.session.add(contact)
            db.session.commit()

            # Send confirmation email
            send_query_contact_email(
                to_email=email,
                username=username,
                query_details=queries
            )

            return jsonify({
                'status': 'success',
                'message': 'Your message has been sent! A confirmation email has been sent to you.',
                'data': {
                    'username':username,
                    'email': email,
                    'phone_number': phone_number,
                    'queries': queries,
                    'user_id': user_id
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            print("Error during contact creation:", e)  # Debugging statement
            return jsonify({
                'status': 'error',
                'message': f'An error occurred: {e}'
            }), 500

    return jsonify({
        'status': 'error',
        'message': 'GET method not supported. Please send a POST request.'
    }), 405




def allowed_file(filename):
>>>>>>> Stashed changes
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}