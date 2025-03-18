from flask import Blueprint, request, jsonify
from models import db, User
import re
from datetime import datetime, timedelta, timezone
import jwt
from flask import current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    device_id = data.get('device_id')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    location = data.get('location')

    # Validasi data tidak boleh kosong
    if not all([device_id, username, email, password, location]):
        return jsonify({"error": "Semua kolom harus diisi!"}), 400

    # Validasi email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Gunakan email yang valid!"}), 400

    # Cek apakah email atau username sudah terdaftar
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email telah digunakan!"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username telah digunakan!"}), 400
    if User.query.filter_by(device_id=device_id).first():
        return jsonify({"error": "Device ID telah digunakan!"}), 400

    # Hash password sebelum disimpan
    user = User(device_id=device_id, username=username, email=email, location=location)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registrasi berhasil!"}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email dan password harus diisi!"}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Generate token dengan masa berlaku 6 bulan
        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.now(timezone.utc) + timedelta(days=180)   # 6 bulan = 180 hari
            },
            current_app.config["SECRET_KEY"],  # Secret key dari konfigurasi Flask
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