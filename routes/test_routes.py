from flask import Blueprint, request
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from models.models import db

test_bp = Blueprint('test', __name__)
    
@test_bp.route('/simple_test', methods=['GET'])
def simple_test():
    print("Simple test route hit")
    return "Simple test works!"

@test_bp.route('/test_port')
def test_port():
    return "Test route works!"

@test_bp.route('/test_get', methods=['POST'])
def test_get():
    print("POST request received on /test_get")
    return "POST request received", 200



@test_bp.route('/test_app', methods=['GET'])
def test_app():
    return "Test route works!"