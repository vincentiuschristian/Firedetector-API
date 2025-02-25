from flask import Flask, jsonify
from database import create_app
from models import db, SensorData
from mqtt_handler import start_mqtt

app = create_app()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running!"})

@app.route('/api/latest', methods=['GET'])
def get_latest_data():
    latest_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    if latest_data:
        return jsonify({
            "temperature": latest_data.temperature,
            "humidity": latest_data.humidity,
            "mq_status": latest_data.mq_status,
            "flame_status": latest_data.flame_status,
            "timestamp": latest_data.timestamp
        })
    else:
        return jsonify({"message": "No data found"}), 404

if __name__ == '__main__':
    start_mqtt()  # Mulai MQTT listener
    app.run(host='0.0.0.0', port=5000, debug=True)



