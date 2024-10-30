import os
import pytest
from flask import Flask
from app import app
from db.db import get_db_connection  # Import your direct DB connection function
from config.config import Config
from routes.auth_routes import User
import random
import string
import time
import random
import string
import time
from unittest.mock import patch, ANY
import random

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
        # Cleanup logic after tests
        cleanup_test_users()

def cleanup_test_users():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Delete test users. Adjust this query according to your requirements.
            cursor.execute("DELETE FROM users WHERE email LIKE 'test%@example.com'")
            connection.commit()
        except Exception as e:
            print(f"Cleanup failed: {e}")
        finally:
            cursor.close()
            connection.close()



# Helper function to generate unique email
def generate_unique_email():
    timestamp = int(time.time())
    return f"testuser_{timestamp}@gmail.com"

# Helper function to generate a unique phone number
def generate_unique_phone():
    return "1234" + ''.join(random.choices(string.digits, k=6))

# @patch('utils.email_utils.send_otp_email')
# def test_register_success(mock_send_email, client):
#     # mock_send_email.return_value = True  # Mock email sending to do nothing
#     mock_send_email.side_effect = lambda *args, **kwargs: print("Mock email sent!")  # Debugging line
#     response = client.post('/api/register', json={
#         'username': 'testuser_' + str(random.randint(1000, 9999)),  # Random suffix for uniqueness
#         'email': generate_unique_email(),
#         'phone_number': generate_unique_phone(),
#         'password': 'Password@123',
#         'confirm_password': 'Password@123'
#     })

#     print(response.json)  # Log the full response
#     assert response.status_code == 201
#     assert response.json['status'] == 'success'
#     assert 'User registered successfully' in response.json['message']



@patch('routes.auth_routes.send_otp_email')  # Adjust path if needed
def test_register_success(mock_send_email, client):
    # Mocking the send_otp_email to print a message instead of sending an email
    mock_send_email.side_effect = lambda *args, **kwargs: print("Mock email sent!")

    # Unique user data for testing
    user_data = {
        'username': f'testuser_{random.randint(1000, 9999)}',  # Random suffix for uniqueness
        'email': generate_unique_email(),
        'phone_number': generate_unique_phone(),
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    }

    # Act: Make a POST request to the register endpoint
    response = client.post('/api/register', json=user_data)
    
    # Debugging output to log the response content
    print(response.json)

    # Assert: Verify the response status and content
    assert response.status_code == 201
    assert response.json['status'] == 'success'
    assert 'User registered successfully' in response.json['message']

    # Confirm that the send_otp_email was called exactly once
    mock_send_email.assert_called_once_with(to_email=user_data['email'], otp=ANY)

def test_register_password_validation_failure(client):
    response = client.post('/api/register', json={
        'username': 'testuser_' + str(random.randint(1000, 9999)),
        'email': generate_unique_email(),
        'phone_number': generate_unique_phone(),
        'password': 'pass',  # Weak password
        'confirm_password': 'pass'
    })
    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert "Password does not meet the requirements." in response.json['message']

def test_register_password_mismatch(client):
    response = client.post('/api/register', json={
        'username': 'testuser_' + str(random.randint(1000, 9999)),
        'email': generate_unique_email(),
        'phone_number': generate_unique_phone(),
        'password': 'Password@123',
        'confirm_password': 'Wrongpassword@123'  # Passwords do not match
    })
    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert "Passwords do not match." in response.json['message']

def test_register_email_exists(client):
    # First register the user
    unique_email = generate_unique_email()
    client.post('/api/register', json={
        'username': 'testuser_' + str(random.randint(1000, 9999)),
        'email': unique_email,
        'phone_number': generate_unique_phone(),
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    })

    # Try registering again with the same email
    response = client.post('/api/register', json={
        'username': 'testuser_' + str(random.randint(1000, 9999)),
        'email': unique_email,  # Same email as before
        'phone_number': generate_unique_phone(),
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    })
    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert "Email already exists in the main user database." in response.json['message']

def test_register_phone_exists(client):
    # First register the user
    unique_phone = generate_unique_phone()
    client.post('/api/register', json={
        'username': 'testuser_' + str(random.randint(1000, 9999)),
        'email': generate_unique_email(),
        'phone_number': unique_phone,
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    })

    # Try registering again with the same phone number
    response = client.post('/api/register', json={
        'username': 'testuser_' + str(random.randint(1000, 9999)),
        'email': generate_unique_email(),
        'phone_number': unique_phone,  # Same phone number as before
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    })
    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert "Phone number already exists in the main user database." in response.json['message']
