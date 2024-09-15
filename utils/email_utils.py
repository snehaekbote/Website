from flask import Blueprint, g, render_template, request, session,current_app as app, jsonify, send_file
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import Config
import logging

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



def send_career_email(to_email, username, profile, resume_filename, application_id):
    # Create the email body as a string
    body = f"""
    Dear {username},

    Thank you for applying for the position of {profile} at Turtu India LLP.

    We have successfully received your application. Below are the details of your submission:

    - Application ID: {application_id}
    - Position Applied: {profile}
    - Resume File: {resume_filename}

    Our HR team is currently reviewing your application. If your qualifications match the job requirements, we will contact you to schedule the next steps in the hiring process.

    Thank you for your interest in joining Turtu India LLP.

    Best regards,
    The Turtu India LLP Team
    """

    # Create the MIME message
    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'plain'))  # Attach the plain text email content
    msg['Subject'] = 'Job Application Confirmation - Turtu India LLP'
    msg['From'] = Config.SMTP_USERNAME
    msg['To'] = to_email

    try:
        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)
        print("Confirmation email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

def send_query_contact_email(to_email, username, query_details):
    with app.app_context():
        # Construct the body of the email with the username and query details
        body = f"""
        <html>
            <body>
                <p>Dear {username},</p>
                <p>Thank you for reaching out to us with your query. We have received your message and will respond as soon as possible.</p>
                <p><strong>Your Query:</strong></p>
                <p>{query_details}</p>
                <p>Best Regards,<br>Turtu India LLP Support Team</p>
            </body>
        </html>
        """

    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'html'))
    msg['Subject'] = 'We have received your query'
    msg['From'] = Config.SMTP_USERNAME
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)
        print("Query confirmation email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

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

def send_password_reset_email(to_email, reset_link):
    try:
        print("Entering send_password_reset_email function...")  # Debugging
        print(f"Reset link: {reset_link}")  # Debugging

        body = f"""
        <p>You have requested a password reset. Click the link below to reset your password:</p>
        <p><a href="{reset_link}">Reset Password</a></p>
        """
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