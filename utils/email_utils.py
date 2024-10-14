from flask import Blueprint, g, render_template, request, session,current_app as app, jsonify, send_file
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import Config
import logging
from email.mime.base import MIMEBase
from email import encoders

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



def send_career_email(to_email, username, profile, resume_filename, resume_data):
    # Create the email body using HTML
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #333;">Dear {username},</h2>
            <p style="font-size: 16px; color: #555;">
                Thank you for applying for the position of <strong>{profile}</strong> at <strong style="color: #0078D4;">Turtu</strong>.
            </p>
            <p style="font-size: 16px; color: #555;">
                We are pleased to inform you that we have successfully received your application. Here are the details of your submission:
            </p>
            <ul style="font-size: 16px; color: #555; line-height: 1.6;">
                <li><strong>Position Applied:</strong> {profile}</li>
                <li><strong>Resume File:</strong> {resume_filename}</li>
            </ul>
            <p style="font-size: 16px; color: #555;">
                Our HR team is currently reviewing your application. If your qualifications match the job requirements, we will reach out to schedule the next steps in the hiring process.
            </p>
            <p style="font-size: 16px; color: #555;">
                Thank you for your interest in joining <strong style="color: #0078D4;">Turtu</strong>. We appreciate the time and effort you put into your application.
            </p>
            <p style="font-size: 16px; color: #333; font-weight: bold;">
                Best regards,<br>
                The Turtu Team
            </p>
        </div>
    </body>
    </html>
    """

    # Create the MIME message
    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'html'))  # Attach the HTML email content
    msg['Subject'] = 'Job Application Confirmation - Turtu'
    msg['From'] = Config.SMTP_USERNAME
    msg['To'] = to_email

    # Adding the resume as an attachment
    if resume_data:
        # Create MIMEBase object for the attachment
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(resume_data)  # Attach the binary resume data
        encoders.encode_base64(part)  # Encode the payload in Base64

        # Add the header with the resume filename
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{resume_filename}"'
        )

        # Attach the resume to the email
        msg.attach(part)

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
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="margin: 20px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f9f9f9;">
                    <p style="font-size: 18px;">Dear <strong>{username}</strong>,</p>
                    <p>Thank you for reaching out to us with your query. We have received your message and will respond as soon as possible.</p>
                    <p style="font-weight: bold;">Your Query:</p>
                    <p style="border-left: 4px solid #007bff; padding-left: 10px;">{query_details}</p>
                    <p>Best Regards,<br><strong>Turtu Support Team</strong></p>
                </div>
            </body>
        </html>
        """

    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'html'))
    msg['Subject'] = 'We Have Received Your Query'
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

def send_otp_email(to_email, otp):
    with app.app_context():
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="margin: 20px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f9f9f9;">
                    <p style="font-size: 18px;">Hello,</p>
                    <p>Your OTP for login is: <strong style="font-size: 24px; color: #007bff;">{otp}</strong></p>
                    <p>If you did not request this, please ignore this email.</p>
                    <p>Thank you,<br><strong>Turtu Support Team</strong></p>
                </div>
            </body>
        </html>
        """
    msg = MIMEText(body, 'html')
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = Config.SMTP_USERNAME
    msg['To'] = to_email

    try:
        # Connect to SMTP server
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        
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

        # Construct the email body with styling
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="margin: 20px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f9f9f9;">
                    <p style="font-size: 18px;">You have requested a password reset. Please click the link below to reset your password:</p>
                    <p>
                        <a href="{reset_link}" style="padding: 10px 15px; background-color: #007bff; color: #ffffff; text-decoration: none; border-radius: 5px;">
                            Reset Password
                        </a>
                    </p>
                    <p style="font-size: 14px; color: #666;">If you did not request a password reset, please ignore this email.</p>
                    <p>Best Regards,<br><strong>Turtu Support Team</strong></p>
                </div>
            </body>
        </html>
        """
    except Exception as e:
        print(f"Error in constructing email body: {e}")  # Log the exception
        return  # Exit the function if there's an error

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
