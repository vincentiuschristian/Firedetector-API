# auth/token_required.py
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from models import User

SECRET_KEY_USER = "user_secret_key"
SECRET_KEY_FIREFIGHTER = "firefighter_secret_key"

def token_required_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Ambil token dari header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            # Decode token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # Dapatkan user dari database
            current_user = User.query.get(data['user_id'])
            
            # Validasi user dan token
            if not current_user or current_user.token != token:
                return jsonify({'error': 'Invalid token!'}), 401
                
            # Tambahkan pengecekan role jika diperlukan
            if f.__name__ in ['firefighter_only_endpoint'] and not current_user.is_firefighter:
                return jsonify({'error': 'Firefighter access only!'}), 403

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        return f(current_user, *args, **kwargs)
    return decorated

def token_required_firefighter(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            
            if not current_user or current_user.token != token:
                return jsonify({'error': 'Invalid token!'}), 401
                
            if not current_user.is_firefighter:
                return jsonify({'error': 'Firefighter access only!'}), 403

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        return f(current_user, *args, **kwargs)
    return decorated
