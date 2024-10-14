from flask import current_app, Blueprint, g, request, jsonify
from flask import send_file
import io
import os
from werkzeug.utils import secure_filename
from utils.email_utils import send_career_email, send_query_contact_email
from models.models import db, CareerApplication, Contact
import jwt
from functools import wraps
from werkzeug.exceptions import RequestEntityTooLarge
from config.config import Config
import mimetypes


user_bp = Blueprint('user', __name__)

# Utility function to extract and decode JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if 'Authorization' exists in request headers
        if 'Authorization' in request.headers:
            # Log the entire Authorization header for debugging
            print(f"Authorization Header: {request.headers['Authorization']}")
            
            # Split 'Bearer <token>' and extract the token
            token = request.headers['Authorization'].split(" ")[1]

        # If token is missing, return an error
        if not token:
            print("Token is missing!")
            return jsonify({
                'status': 'error',
                'message': 'Token is missing!'
            }), 401

        try:
            # Decode the token using the secret key and the HS256 algorithm
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            print(f"Decoded token data: {data}")  # Debugging decoded data

            # Store the decoded user information in Flask's global `g` object
            g.user = data
        except jwt.ExpiredSignatureError:
            print("Token has expired!")
            return jsonify({
                'status': 'error',
                'message': 'Token has expired. Please log in again.'
            }), 401
        except jwt.InvalidTokenError:
            print("Invalid token!")
            return jsonify({
                'status': 'error',
                'message': 'Invalid token. Please log in again.'
            }), 401

        # If token is valid, proceed with the route function
        return f(*args, **kwargs)

    return decorated

# Sample route to verify the token
@user_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    return jsonify({
        'message': 'Token is valid!',
        'user': g.user  # Accessing the user info stored in g during token verification
    }), 200


# @user_bp.route('/career', methods=['POST'])
# @token_required  # Apply the JWT decorator
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
#             # Use the decoded token data stored in g.user (from the decorator)
#             user_data = g.user  # This will contain the decoded user data from the token
#             user_id = user_data.get('user_id')  # Assuming the token contains 'id' for user
           
#             # Construct the full URL for the resume
#             resume_url = f'https://www.server.turtu.in/uploads/{filename}'  # Change 'your-domain.com' to your actual domain

#             # Create a new career application entry
#             application = CareerApplication(
#                 user_id=user_id,
#                 email=email,
#                 phone_number=phone_number,
#                 profile=profile,
#                 resume_filename=resume_url
#             )
#             db.session.add(application)
#             db.session.commit()

#             # Optional: Send a confirmation email after saving the application
#             send_career_email(
#                 to_email=email,
#                 username=user_data.get('username'),  # Extract from token
#                 profile=profile,
#                 resume_filename=resume_url
#             )

#             # Respond with the application and user info
#             return jsonify({
#                 'status': 'success',
#                 'message': 'Application submitted successfully!',
#                 'data': {
#                     'user_id': user_id,
#                     'email': email,
#                     'phone_number': phone_number,
#                     'profile': profile,
#                     'resume_filename': resume_url,
#                     'user_data': user_data  # Send back decoded token info if needed
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

# @user_bp.route('/career-applications', methods=['GET'])
# def get_career_applications():
#     try:
#         # Fetch all career applications from the database
#         applications = CareerApplication.query.all()
        
#         # Create a list of dictionaries for the response
#         application_list = [{
#             'id': app.id,
#             'email': app.email,
#             'phone_number': app.phone_number,
#             'profile': app.profile,
#             'resume_filename': app.resume_filename,
#             'created_at': app.created_at.strftime('%Y-%m-%d %H:%M:%S')
#         } for app in applications]

#         return jsonify({
#             'status': 'success',
#             'data': application_list
#         }), 200
#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': f'An error occurred: {e}'
#         }), 500

# from flask import send_from_directory

# @user_bp.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory('uploads', filename)



# @user_bp.route('/career', methods=['POST'])
# @token_required  # Apply the JWT decorator
# def career():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         phone_number = request.form.get('phone_number')
#         profile = request.form.get('profile')
#         resume = request.files.get('resume')

#         print("Request Form:", request.form)
#         print("Request Files:", request.files)

#         if not email or not phone_number or not profile or not resume:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'All fields are required.'
#             }), 400

#         if resume and allowed_file(resume.filename):
#             print(f"Uploaded file size: {resume.content_length} bytes")  # Check content length
            
#             # Check the size of the uploaded resume file
#             MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB in bytes
#             if resume.content_length > MAX_FILE_SIZE:
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'File size exceeds the maximum limit of 1 MB.'
#                 }), 400
            
#             # Secure the filename
#             filename = secure_filename(resume.filename)

#             # Read file contents as binary data
#             resume_data = resume.read()
#             print(f"Resume Data Size After Read: {len(resume_data)} bytes")  # Check size after reading

#             # Check if resume_data is empty after read
#             if not resume_data:
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'Uploaded file data is empty.'
#                 }), 400

#             try:
#                 user_data = g.user
#                 user_id = user_data.get('user_id')
                
#                 # Create a new career application entry with BLOB
#                 application = CareerApplication(
#                     user_id=user_id,
#                     email=email,
#                     phone_number=phone_number,
#                     profile=profile,
#                     resume_filename=filename,
#                     resume_data=resume_data  # Store BLOB data
#                 )
#                 db.session.add(application)
#                 db.session.commit()

#                 return jsonify({
#                     'status': 'success',
#                     'message': 'Application submitted successfully!'
#                 }), 201
#             except Exception as e:
#                 db.session.rollback()
#                 print(f"Error occurred: {e}")  # Log the error
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'An error occurred while saving your application.'
#                 }), 500
#         else:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Invalid file format for resume.'
#             }), 400



@user_bp.route('/career', methods=['POST'])
@token_required  # Apply the JWT decorator
def career():
    if request.method == 'POST':
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        profile = request.form.get('profile')
        resume = request.files.get('resume')

        print("Request Form:", request.form)
        print("Request Files:", request.files)

        if not email or not phone_number or not profile or not resume:
            return jsonify({
                'status': 'error',
                'message': 'All fields are required.'
            }), 400

        if resume and allowed_file(resume.filename):
            # Secure the filename
            filename = secure_filename(resume.filename)

            # Read file contents as binary data
            resume_data = resume.read()
            print(f"Resume Data Size After Read: {len(resume_data)} bytes")  # Check size after reading

            if not resume_data:
                return jsonify({
                    'status': 'error',
                    'message': 'Uploaded file data is empty.'
                }), 400

            try:
                user_data = g.user
                user_id = user_data.get('user_id')
                
                # Create a new career application entry with BLOB
                application = CareerApplication(
                    user_id=user_id,
                    email=email,
                    phone_number=phone_number,
                    profile=profile,
                    resume_filename=filename,
                    resume_data=resume_data  # Store BLOB data
                )
                db.session.add(application)
                db.session.commit()

                # Send career application email after submission
                send_career_email(to_email=email, username=user_data.get('username'), profile=profile, resume_filename=filename, resume_data=resume_data)


                return jsonify({
                    'status': 'success',
                    'message': 'Application submitted successfully! A confirmation email has been sent.'
                }), 201
            except Exception as e:
                db.session.rollback()
                print(f"Error occurred: {e}")
                return jsonify({
                    'status': 'error',
                    'message': 'An error occurred while saving your application.'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid file format for resume.'
            }), 400

@user_bp.route('/career-applications', methods=['GET'])
def get_career_applications():
    try:
        # Fetch all career applications from the database
        applications = CareerApplication.query.all()

        # Create a list of dictionaries for the response
        application_list = [{
            'id': app.id,
            'email': app.email,
            'phone_number': app.phone_number,
            'profile': app.profile,
            'resume_filename': app.resume_filename,
            'created_at': app.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for app in applications]

        return jsonify({
            'status': 'success',
            'data': application_list
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {e}'
        }), 500


# @user_bp.route('/career-applications/<int:application_id>/resume', methods=['GET'])
# def download_resume(application_id):
#     try:
#         # Fetch the application by id
#         application = CareerApplication.query.get(application_id)
#         if not application:
#             return jsonify({'status': 'error', 'message': 'Application not found'}), 404

#         # Serve the resume as a downloadable file
#         return send_file(
#             io.BytesIO(application.resume_data),
#             mimetype='application/pdf',  # You can adjust based on the file type
#             download_name=application.resume_filename,
#             as_attachment=False
#         )
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': f'An error occurred: {e}'}), 500

@user_bp.route('/career-applications/<int:application_id>/resume', methods=['GET'])
def download_resume(application_id):
    try:
        # Fetch the application by id
        application = CareerApplication.query.get(application_id)
        if not application:
            return jsonify({'status': 'error', 'message': 'Application not found'}), 404

        # Get the MIME type of the resume based on the filename
        mime_type, _ = mimetypes.guess_type(application.resume_filename)

        # Serve the resume as a viewable file (not a download)
        response = send_file(
            io.BytesIO(application.resume_data),
            mimetype=mime_type or 'application/octet-stream',  # Fallback to generic if unknown
            download_name=application.resume_filename,
            as_attachment=False  # False ensures the file is not forced to download
        )
        
        # Explicitly set Content-Disposition to 'inline'
        response.headers["Content-Disposition"] = f"inline; filename={application.resume_filename}"

        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'An error occurred: {e}'}), 500


@user_bp.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        # Retrieve form data (email, phone number, and queries)
        username = request.json.get('username')
        email = request.json.get('email')
        phone_number = request.json.get('phone_number')
        queries = request.json.get('queries')

        # Check if all required fields are provided
        if not username or not email or not phone_number or not queries:
            return jsonify({
                'status': 'error',
                'message': 'All fields are required.'
            }), 400

        try:
            # Create a new contact entry without user_id and username
            contact_entry = Contact(
                username=username,
                email=email,
                phone_number=phone_number,
                queries=queries
            )
            db.session.add(contact_entry)
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
                    'username': username,
                    'email': email,
                    'phone_number': phone_number,
                    'queries': queries
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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}

@user_bp.route('/contact-queries', methods=['GET'])
def get_contact_queries():
    try:
        # Fetch all contact entries from the database
        contacts = Contact.query.all()
        
        # Create a list of dictionaries for the response
        contact_list = [{
            'id': contact.id,
            'username': contact.username,
            'email': contact.email,
            'phone_number': contact.phone_number,
            'queries': contact.queries,
            'created_at': contact.created_at 
        } for contact in contacts]

        return jsonify({
            'status': 'success',
            'data': contact_list
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {e}'
        }), 500
