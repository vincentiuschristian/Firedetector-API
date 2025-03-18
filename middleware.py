import jwt
from flask import request, jsonify
from functools import wraps
from config import Config
from models import User

SECRET_KEY = Config.SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Ambil token dari header Authorization
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token tidak ditemukan!"}), 401

        try:
            # Decode token untuk mendapatkan user_id
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])

            if not current_user:
                return jsonify({"error": "User tidak ditemukan!"}), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token sudah expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token tidak valid!"}), 401

        # Jika token valid, lanjutkan request
        return f(current_user, *args, **kwargs)
    
    return decorated
