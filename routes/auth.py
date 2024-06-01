from flask import Blueprint, request, jsonify
from models import Person
from utils import generate_password_hash, check_password_hash, generate_token
from neomodel.exceptions import UniqueProperty

auth_blueprint = Blueprint('auth', __name__)

def validate_register_data(data, required_fields):
    missing_or_empty_fields = [field for field in required_fields if field not in data or data[field] == ""]
    if missing_or_empty_fields:
        return False, f"Missing or empty fields: {', '.join(missing_or_empty_fields)}"
    return True, None
@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['first_name', 'last_name', 'phone', 'email', 'role', 'password']
    # Validate incoming data
    is_valid, error_message = validate_register_data(data,required_fields)
    if not is_valid:
        return jsonify({'message': error_message}), 401

    try:
        hashed_password = generate_password_hash(data['password'])
        person = Person(
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email=data['email'],
            role=data['role'],
            password=hashed_password
        )
        person.save()
        return jsonify({'message': 'User registered successfully'}), 201

    except UniqueProperty:
        return jsonify({'message': 'Phone or email already exists'}), 401

    except Exception as e:
        return jsonify({'message': 'An error occurred while registering the user', 'error': str(e)}), 500

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    required_fields = [ 'email', 'password']
    is_valid, error_message = validate_register_data(data,required_fields)
    if not is_valid:
        return jsonify({'message': error_message}), 401
    try:
        person = Person.nodes.get(email=data['email'])
        if person and check_password_hash(data['password'], person.password):
            token = generate_token(person.uid,person.role)
            return jsonify({'token': token}), 200
        return jsonify({'message': 'Invalid credentials'}), 401
    except Person.DoesNotExist:
        return jsonify({'message': 'Invalid credentials'}), 401
