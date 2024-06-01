from flask import Blueprint, request, jsonify
from models import  Person
from utils import token_required, validate_data

# Create a blueprint
users_blueprint = Blueprint('users', __name__)

@users_blueprint.route('/user', methods=['GET'])
@token_required
def get_user(current_user_id):
    try:
        person = Person.nodes.get(uid=current_user_id)
        return jsonify(person.to_dict()), 200
    except Person.DoesNotExist:
        return jsonify({'message': 'User not found'})


#Update UserData
@users_blueprint.route('/user', methods=['PUT'])
@token_required
def update_user(current_user_id):
    data = request.get_json()
    required_fields = ['first_name', 'last_name', 'phone']
    is_valid, error_message = validate_data(data, required_fields)
    if not is_valid:
        return jsonify({'message': error_message}), 400
    try:
        person = Person.nodes.get(uid=current_user_id)
        person.first_name = data['first_name']
        person.last_name = data['last_name']
        person.phone = data['phone']
        person.save()
        return jsonify(person.to_dict()), 200
    except Person.DoesNotExist:
        return jsonify({'message': 'User not found'}), 404

#Change Password
@users_blueprint.route('/user/change-password', methods=['PUT'])
@token_required
def change_password(current_user_id):
    data = request.get_json()
    required_fields = ['password']
    is_valid, error_message = validate_data(data, required_fields)
    if not is_valid:
        return jsonify({'message': error_message}), 400
    try:
        person = Person.nodes.get(uid=current_user_id)
        person.password = data['password']
        person.save()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Person.DoesNotExist:
        return jsonify({'message': 'User not found'}), 404
    