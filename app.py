from flask import Flask, jsonify
from database import create_app, db
from models import SensorData, User
from mqtt_handler import start_mqtt
from auth import auth_bp
from middleware import token_required
from config import Config

app = create_app()

# 🔥 Pastikan db sudah terikat ke app sebelum digunakan
with app.app_context():
    db.create_all()

app.register_blueprint(auth_bp)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running!"})

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    user = User.query.filter_by(id=current_user.id).first()
    
    if user:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({"message": "User tidak ditemukan!"}), 404

@app.route('/api/sensor/latest', methods=['GET'])
@token_required
def get_latest_sensor_data(current_user):
    latest_data = SensorData.query.order_by(SensorData.id.desc()).first()

    if latest_data:
        return jsonify({
            "id": latest_data.id,
            "temperature": latest_data.temperature,
            "humidity": latest_data.humidity,
            "mq_status": latest_data.mq_status,
            "flame_status": latest_data.flame_status,
            "timestamp": latest_data.timestamp.isoformat() if latest_data.timestamp else None
        })
    else:
        return jsonify({"message": "No data found"}), 404

@app.route('/api/sensor/history', methods=['GET'])
@token_required
def get_sensor_history(current_user):
    history_data = SensorData.query.order_by(SensorData.id.desc()).limit(100).all()

    if history_data:
        return jsonify([
            {
                "id": data.id,
                "temperature": data.temperature,
                "humidity": data.humidity,
                "mq_status": data.mq_status,
                "flame_status": data.flame_status,
                "timestamp": data.timestamp.isoformat() if data.timestamp else None
            }
            for data in history_data
        ])
    else:
        return jsonify({"message": "No history data found"}), 404

if __name__ == '__main__':
    with app.app_context():
        start_mqtt()
    app.run(host='0.0.0.0', port=5000, debug=True)
