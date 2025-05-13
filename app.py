from flask import Flask, jsonify
from models import RuangTamuData, KamarData 
from datetime import datetime
from database import create_app, db
from models import User
from mqtt_handler import start_mqtt
from auth import auth_bp
from middleware import token_required
from config import Config
from flask_migrate import Migrate
from location import locations_bp

app = create_app()
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

app.register_blueprint(auth_bp)
app.register_blueprint(locations_bp)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running!"})

@app.route('/api/ruangtamu/latest', methods=['GET'])
@token_required
def get_latest_ruangtamu(current_user):
    latest_data = RuangTamuData.query.order_by(RuangTamuData.id.desc()).first()
    if latest_data:
        return jsonify({
            "id": latest_data.id,
            "temperature": latest_data.temperature,
            "humidity": latest_data.humidity,
            "mq_status": latest_data.mq_status,
            "flame_status": latest_data.flame_status,
            "timestamp": latest_data.timestamp.isoformat()
        })
    return jsonify({"message": "No data found"}), 404

@app.route('/api/kamar/latest', methods=['GET'])
@token_required
def get_latest_kamar(current_user):
    latest_data = KamarData.query.order_by(KamarData.id.desc()).first()
    if latest_data:
        return jsonify({
            "id": latest_data.id,
            "temperature": latest_data.temperature,
            "humidity": latest_data.humidity,
            "mq_status": latest_data.mq_status,
            "flame_status": latest_data.flame_status,
            "timestamp": latest_data.timestamp.isoformat()
        })
    return jsonify({"message": "No data found"}), 404

@app.route('/api/ruangtamu/history', methods=['GET'])
@token_required
def get_ruangtamu_history(current_user):
    data = RuangTamuData.query.order_by(RuangTamuData.id.desc()).limit(100).all()
    return jsonify([{
        "id": d.id,
        "temperature": d.temperature,
        "humidity": d.humidity,
        "mq_status": d.mq_status,
        "flame_status": d.flame_status,
        "timestamp": d.timestamp.isoformat()
    } for d in data])

@app.route('/api/kamar/history', methods=['GET'])
@token_required
def get_kamar_history(current_user):
    data = KamarData.query.order_by(KamarData.id.desc()).limit(100).all()
    return jsonify([{
        "id": d.id,
        "temperature": d.temperature,
        "humidity": d.humidity,
        "mq_status": d.mq_status,
        "flame_status": d.flame_status,
        "timestamp": d.timestamp.isoformat()
    } for d in data])

if __name__ == '__main__':
    with app.app_context():
        start_mqtt()
    app.run(host='0.0.0.0', port=5000, debug=True)