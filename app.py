from flask import Flask, jsonify
from database import create_app
from models import db, SensorData
from mqtt_handler import start_mqtt
from auth import auth_bp
from flask import Flask, jsonify
from models import db, SensorData
from datetime import datetime

app = create_app()
app.register_blueprint(auth_bp) 
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running!"})

@app.route('/api/sensor/latest', methods=['GET'])
def get_latest_sensor_data():
    # Mengambil 1 data terbaru berdasarkan ID tertinggi
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

# Endpoint untuk mendapatkan semua data history sensor, terbaru di paling atas
@app.route('/api/sensor/history', methods=['GET'])
def get_sensor_history():
    # Urutkan berdasarkan ID secara descending (data terbaru di paling atas)
    history_data = SensorData.query.order_by(SensorData.id.desc()).all()
    
    if history_data:
        return jsonify([{
            "id": data.id,
            "temperature": data.temperature,
            "humidity": data.humidity,
            "mq_status": data.mq_status,
            "flame_status": data.flame_status,
            "timestamp": data.timestamp.isoformat() if data.timestamp else None
        } for data in history_data])
    else:
        return jsonify({"message": "No data found"}), 404

if __name__ == '__main__':
    start_mqtt()  # Mulai MQTT listener
    app.run(host='0.0.0.0', port=5000, debug=True)
