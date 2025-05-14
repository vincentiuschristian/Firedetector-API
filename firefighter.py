from flask import Blueprint, request, jsonify, current_app
from models import db, User, RuangTamuData, KamarData, DeviceLocation
from middleware import token_required_firefighter
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

firefighter_bp = Blueprint('firefighter', __name__, url_prefix='/api/firefighter')

@firefighter_bp.route('/register', methods=['POST'])
def register_firefighter():
    data = request.get_json()
    
    required_fields = ['firefighter_id', 'username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "All fields are required",
            "required_fields": required_fields
        }), 400

    # Validasi unik
    errors = {}
    if User.query.filter_by(email=data['email']).first():
        errors['email'] = "Email already registered"
    if User.query.filter_by(username=data['username']).first():
        errors['username'] = "Username already taken"
    if User.query.filter_by(firefighter_id=data['firefighter_id']).first():
        errors['firefighter_id'] = "Firefighter ID already registered"
    
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    try:
        user = User(
            firefighter_id=data['firefighter_id'],
            username=data['username'],
            email=data['email'],
            is_firefighter=True,
            location="Fire Station",
            password_hash=generate_password_hash(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "Firefighter registration successful",
            "user_id": user.id,
            "firefighter_id": user.firefighter_id
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Firefighter registration error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@firefighter_bp.route('/login', methods=['POST'])
def login_firefighter():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data['email'], is_firefighter=True).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "Invalid credentials or not a firefighter account"}), 401

    try:
        # Generate token
        token_payload = {
            "user_id": user.id,
            "is_firefighter": True,
            "exp": datetime.now(timezone.utc) + timedelta(days=1)  # Token expires in 1 day
        }
        
        token = jwt.encode(
            token_payload,
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        
        user.token = token
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "expires_at": token_payload["exp"].isoformat(),
            "user": {
                "id": user.id,
                "firefighter_id": user.firefighter_id,
                "username": user.username,
                "email": user.email
            }
        })

    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@firefighter_bp.route('/all-sensor-data', methods=['GET'])
@token_required_firefighter
def get_all_sensor_data(current_user):
    try:
        users = User.query.options(
            db.joinedload(User.ruang_tamu_data).order_by(RuangTamuData.timestamp.desc()),
            db.joinedload(User.kamar_data).order_by(KamarData.timestamp.desc())
        ).all()
        
        result = []
        for user in users:
            latest_ruang_tamu = user.ruang_tamu_data[0] if user.ruang_tamu_data else None
            latest_kamar = user.kamar_data[0] if user.kamar_data else None
            
            user_data = {
                "user_id": user.id,
                "username": user.username,
                "location": user.location,
                "ruang_tamu": {
                    "temperature": latest_ruang_tamu.temperature if latest_ruang_tamu else None,
                    "humidity": latest_ruang_tamu.humidity if latest_ruang_tamu else None,
                    "mq_status": latest_ruang_tamu.mq_status if latest_ruang_tamu else None,
                    "flame_status": latest_ruang_tamu.flame_status if latest_ruang_tamu else None,
                    "timestamp": latest_ruang_tamu.timestamp.isoformat() if latest_ruang_tamu else None
                },
                "kamar": {
                    "temperature": latest_kamar.temperature if latest_kamar else None,
                    "humidity": latest_kamar.humidity if latest_kamar else None,
                    "mq_status": latest_kamar.mq_status if latest_kamar else None,
                    "flame_status": latest_kamar.flame_status if latest_kamar else None,
                    "timestamp": latest_kamar.timestamp.isoformat() if latest_kamar else None
                }
            }
            result.append(user_data)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error getting sensor data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@firefighter_bp.route('/all-device-locations', methods=['GET'])
@token_required_firefighter
def get_all_device_locations(current_user):
    try:
        devices = DeviceLocation.query.join(User).all()
        
        return jsonify([{
            "user_id": d.user_id,
            "username": d.user.username,
            "device_number": d.device_number,
            "zone_name": d.zone_name,
            "location": d.device_location,
            "coordinates": {
                "latitude": float(d.device_location.split(',')[0]) if d.device_location else None,
                "longitude": float(d.device_location.split(',')[1]) if d.device_location else None
            },
            "last_updated": d.updated_at.isoformat() if d.updated_at else None
        } for d in devices])
        
    except Exception as e:
        current_app.logger.error(f"Error getting device locations: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500