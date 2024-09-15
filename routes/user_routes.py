from flask import Blueprint, g, request, jsonify
import os
from werkzeug.utils import secure_filename
from routes.auth_routes import login_required
from utils.email_utils import send_career_email, send_query_contact_email
from models.models import db, CareerApplication, Contact

user_bp = Blueprint('user', __name__)

@user_bp.route('/career', methods=['POST'])
@login_required  # Ensure the user is logged in
def career():
    if request.method == 'POST':
        user_id = g.user.id
        
        # Retrieve other form data (except email)
        email = request.form.get('email')
        phone_number = request.form.get('phoneNumber')  # Ensure this matches the key used in Postman
        profile = request.form.get('profile')
        resume = request.files.get('resume')

        # Debug print statements
        print(f"User ID (from session): {user_id}")
        print(f"Email (from session): {email}")
        print(f"Phone Number: {phone_number}")
        print(f"Profile: {profile}")
        print(f"Resume: {resume}")

        # Check if all fields (except email) are provided
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
            return jsonify({
                'status': 'error',
                'message': 'Invalid file format for resume.'
            }), 400

        try:
            # Create a new career application entry with the user_id
            application = CareerApplication(
                user_id=user_id,  # Store the logged-in user's ID
                email=email,  # Use the email from g.user
                phone_number=phone_number,
                profile=profile,
                resume_filename=resume_filename  # Ensure this matches the model
            )
            db.session.add(application)
            db.session.commit()
            
            application_id = application.id
            # Send confirmation email after the application is saved
            send_career_email(
                to_email=email, 
                username=g.user.username,  # Assuming g.user contains the username
                profile=profile, 
                resume_filename=resume_filename, 
                application_id=application_id  # Pass the generated application ID
            )
            
            
            return jsonify({
                'status': 'success',
                'message': 'Application submitted successfully!',
                'data': {
                    'user_id': user_id,
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

    return jsonify({
        'status': 'error',
        'message': 'GET method not supported. Please send a POST request.'
    }), 405

# @routes_bp.route('/career', methods=['POST'])
# @login_required
# def career():
#     if request.method == 'POST':
#         # Retrieve form data
#         email = request.form.get('email')
#         phone_number = request.form.get('phoneNumber')  # Ensure this matches the key used in Postman
#         profile = request.form.get('profile')
#         resume = request.files.get('resume')

#         # Debug print statements
#         print(f"Email: {email}")
#         print(f"Phone Number: {phone_number}")
#         print(f"Profile: {profile}")
#         print(f"Resume: {resume}")

#         # Check if all fields are provided
#         if not email or not phone_number or not profile or not resume:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'All fields are required.'
#             }), 400
        
#         # # Check if the user is registered (assuming `User` is your model)
#         # registered_user = User.query.filter_by(email=email).first()

#         # if not registered_user:
#         #     return jsonify({
#         #         'status': 'error',
#         #         'message': 'User is not registered. Please register first.'
#         #     }), 403

#         # Save resume file if it is valid
#         if resume and allowed_file(resume.filename):
#             filename = secure_filename(resume.filename)
#             resume_filename = os.path.join('uploads', filename)
#             resume.save(resume_filename)
#         else:
#             resume_filename = ''

#         try:
#             # Create a new career application entry
#             application = CareerApplication(
#                 email=email,
#                 phone_number=phone_number,
#                 profile=profile,
#                 resume_filename=resume_filename  # Ensure this matches the model
#             )
#             db.session.add(application)
#             db.session.commit()
#             return jsonify({
#                 'status': 'success',
#                 'message': 'Application submitted successfully!',
#                 'data': {
#                     'email': email,
#                     'phone_number': phone_number,
#                     'profile': profile,
#                     'resume_filename': resume_filename
#                 }
#             }), 201
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({
#                 'status': 'error',
#                 'message': f'An error occurred: {e}'
#             }), 500

@user_bp.route('/contact', methods=['POST'])
@login_required  # Ensures that only logged-in users can access this route
def contact():
    if request.method == 'POST':

        user_id = g.user.id
        # Retrieve form data (queries and phone number)
        username = request.form.get('username')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        queries = request.form.get('queries')


        if not username or not email or not phone_number or not queries:
            return jsonify({
                'status': 'error',
                'message': 'All fields are required.'
            }), 400
        

        try:
            # Create a new contact entry using the current user's information
            # Create a new contact entry with the form-provided values
            contact = Contact(
                user_id=user_id,
                username=username,  # Store the provided username
                email=email,        # Store the provided email
                phone_number=phone_number,
                queries=queries
            )
            db.session.add(contact)
            db.session.commit()

            # Call the email function to send a confirmation email after saving the query
            send_query_contact_email(
                to_email=email, 
                username=username, 
                query_details=queries
            )
            return jsonify({
                'status': 'success',
                'message': 'Your message has been sent! A confirmation email has been sent to you.',
                'data': {
                    'user_id': user_id,
                    'username': username,
                    'email': email,
                    'phone_number': phone_number,
                    'queries': queries
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}