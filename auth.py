from flask import Blueprint, request, jsonify, current_app
from models import db, User, DeviceLocation
from datetime import datetime, timedelta, timezone
from middleware import token_required_user
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/user/profile', methods=['GET'])
@token_required_user
def get_user_profile(current_user):
    user = User.query.filter_by(id=current_user.id).first()
    
    if user:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({"message": "User tidak ditemukan!"}), 404

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "Invalid request",
            "message": "Request harus dalam format JSON"
        }), 400
    
    required_fields = ['device_id', 'username', 'email', 'password', 'location']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            "error": "Validation error",
            "message": f"Field berikut harus diisi: {', '.join(missing_fields)}"
        }), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            "error": "Duplicate email",
            "message": "Email sudah terdaftar"
        }), 409
        
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            "error": "Duplicate username",
            "message": "Username sudah digunakan"
        }), 409

    try:
        user = User(
            device_id=data['device_id'],
            username=data['username'],
            email=data['email'],
            location=data['location'],
            is_firefighter=False
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()

        # Buat device default
        for i in range(1, 3):
            device = DeviceLocation(
                user_id=user.id,
                device_number=i,
                zone_name=f"Device {i}"
            )
            db.session.add(device)

        db.session.commit()
        
        return jsonify({
            "message": "Registrasi berhasil",
            "data": {
                "user_id": user.id,
                "username": user.username
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Registration failed",
            "message": f"Gagal melakukan registrasi: {str(e)}"
        }), 500


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "Invalid request",
            "message": "Request harus dalam format JSON"
        }), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            "error": "Validation error",
            "message": "Email dan password harus diisi"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({
            "error": "Authentication failed",
            "message": "Email atau password salah"
        }), 401

    try:
        token_payload = {
            "user_id": user.id,
            "is_firefighter": user.is_firefighter,
            "exp": datetime.now(timezone.utc) + timedelta(days=60) 
        }
        
        token = jwt.encode(
            token_payload,
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        user.token = token
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "token_expires": token_payload["exp"].isoformat(),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_firefighter": user.is_firefighter
            }
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Server error",
            "message": f"Gagal memproses login: {str(e)}"
        }), 500

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
        user = User.query.filter_by(token=token).first()
        if user:
            user.token = None
            db.session.commit()
            return jsonify({"message": "Logout successful"}), 200
    
    return jsonify({"error": "Invalid token"}), 401