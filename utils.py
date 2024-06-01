import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
from config import JWT_SECRET_KEY
from models import Person

def generate_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password_hash(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token(user_id, role):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': user_id,
        'role': role
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')


def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            current_user_id = decode_token(token)
        except Exception as e:
            return jsonify({'message': str(e)}), 403
        return f(current_user_id, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            current_user_id = decode_token(token)
            current_user = Person.nodes.get(uid=current_user_id)
            if current_user.role != 'admin':
                return jsonify({'message': 'Admin privilege required!'}), 403
        except Exception as e:
            return jsonify({'message': str(e)}), 403
        return f(current_user_id, *args, **kwargs)
    return decorated

def validate_data(data, required_fields):
    missing_or_empty_fields = [field for field in required_fields if field not in data or data[field] == ""]
    if missing_or_empty_fields:
        return False, f"Missing or empty fields: {', '.join(missing_or_empty_fields)}"
    return True, None