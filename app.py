from flask import Flask, jsonify
from database import create_app
from models import db
from mqtt_handler import start_mqtt
from auth import auth_bp  # Import Blueprint untuk autentikasi

app = create_app()
app.register_blueprint(auth_bp)  # Daftarkan Blueprint untuk register dan login

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running!"})

if __name__ == '__main__':
    start_mqtt()  # Mulai MQTT listener
    app.run(host='0.0.0.0', port=5000, debug=True)



