from flask import Flask, jsonify
from models import RuangTamuData, KamarData 
from datetime import datetime
from database import create_app, db
from mqtt_handler import start_mqtt
from auth import auth_bp
from middleware import token_required_user, token_required_firefighter
from flask_migrate import Migrate
from location import locations_bp
from firefighter import firefighter_bp

app = create_app()
migrate = Migrate(app, db)

app.register_blueprint(auth_bp)
app.register_blueprint(locations_bp)
app.register_blueprint(firefighter_bp)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running!"})

@app.route('/api/ruangtamu/latest', methods=['GET'])
@token_required_user
def get_latest_ruangtamu(current_user):
    try:
        latest_data = RuangTamuData.query.order_by(RuangTamuData.timestamp.desc()).first()
        
        if not latest_data:
            return jsonify({
                "error": "Data not found",
                "message": "Belum ada data sensor yang tercatat"
            }), 404
            
        return jsonify({
            "id": latest_data.id,
            "temperature": latest_data.temperature,
            "humidity": latest_data.humidity,
            "mq_status": latest_data.mq_status,
            "flame_status": latest_data.flame_status,
            "timestamp": latest_data.timestamp.isoformat()
        })
    except Exception as e:
        return jsonify({
            "error": "Server error",
            "message": "Gagal mengambil data sensor terbaru",
            "details": str(e)
        }), 500

@app.route('/api/kamar/latest', methods=['GET'])
@token_required_user
def get_latest_kamar(current_user):
    try:
        latest_data = KamarData.query.order_by(KamarData.timestamp.desc()).first()
        
        if not latest_data:
            return jsonify({
                "error": "Data not found", 
                "message": "Belum ada data sensor yang tercatat"
            }), 404
            
        return jsonify({
            "id": latest_data.id,
            "temperature": latest_data.temperature,
            "humidity": latest_data.humidity,
            "mq_status": latest_data.mq_status,
            "flame_status": latest_data.flame_status,
            "timestamp": latest_data.timestamp.isoformat()
        })
    except Exception as e:
        return jsonify({
            "error": "Server error",
            "message": "Gagal mengambil data sensor terbaru",
            "details": str(e)
        }), 500

@app.route('/api/ruangtamu/history', methods=['GET'])
@token_required_user
def get_ruangtamu_history(current_user):
    try:
        data = RuangTamuData.query.order_by(
            RuangTamuData.timestamp.desc()
        ).limit(100).all()
        
        if not data:
            return jsonify({
                "error": "Data not found",
                "message": "Belum ada riwayat sensor yang tercatat"
            }), 404
        
        return jsonify([{
            "id": d.id,
            "user_id": d.user_id,
            "temperature": d.temperature,
            "humidity": d.humidity,
            "mq_status": d.mq_status,
            "flame_status": d.flame_status,
            "timestamp": d.timestamp.isoformat()
        } for d in data])
    except Exception as e:
        return jsonify({
            "error": "Server error",
            "message": "Gagal mengambil riwayat sensor",
            "details": str(e)
        }), 500

@app.route('/api/kamar/history', methods=['GET'])
@token_required_user
def get_kamar_history(current_user):
    try:
        data = KamarData.query.order_by(
            KamarData.timestamp.desc()
        ).limit(100).all()
        
        if not data:
            return jsonify({
                "error": "Data not found",
                "message": "Belum ada riwayat sensor yang tercatat"
            }), 404
            
        return jsonify([{
            "id": d.id,
            "temperature": d.temperature,
            "humidity": d.humidity,
            "mq_status": d.mq_status,
            "flame_status": d.flame_status,
            "timestamp": d.timestamp.isoformat()
        } for d in data])
    except Exception as e:
        return jsonify({
            "error": "Server error",
            "message": "Gagal mengambil riwayat sensor",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        start_mqtt()
    app.run(host='0.0.0.0', port=5000, debug=True)