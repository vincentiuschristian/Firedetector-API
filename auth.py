from flask import Blueprint, request, jsonify
from models import db, User
from models import DeviceLocation
from datetime import datetime, timedelta, timezone
import jwt
from flask import current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required_fields = ['device_id', 'username', 'email', 'password', 'location']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Semua field harus diisi!"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email sudah terdaftar"}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username sudah terdaftar"}), 400

    try:
        user = User(
            device_id=data['device_id'],
            username=data['username'],
            email=data['email'],
            location=data['location']
        )
        user.set_password(data['password'])  
        db.session.add(user)
        db.session.flush()  

        for i in range(1, 3):
            device = DeviceLocation(
                user_id=user.id,
                device_number=i,
                zone_name=f"Alat {i}"
            )
            db.session.add(device)

        db.session.commit()
        
        return jsonify({
            "message": "Registrasi berhasil",
            "user_id": user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email dan password harus diisi!"}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.now(timezone.utc) + timedelta(days=180)  
            },
            current_app.config["SECRET_KEY"],  
            algorithm="HS256"
        )
        return jsonify({
            "message": "Login berhasil!",
            "username": user.username,
            "device_id": user.device_id,
            "token": token  # Kirim token ke client
        }), 200
    else:
        return jsonify({"error": "Email atau password salah!"}), 401