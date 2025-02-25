import paho.mqtt.client as mqtt
import ssl
import json
from flask import Flask
from config import Config
from flask import current_app
from models import db, SensorData  # Import database model

# Inisialisasi Flask app
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Callback ketika berhasil connect
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Successfully connected to MQTT Broker!")
        client.subscribe(Config.MQTT_TOPIC)  # Subscribe ke topik
    else:
        print(f"❌ Failed to connect, return code {rc}")

# Callback ketika menerima pesan
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

    try:
        data_json = json.loads(msg.payload.decode())  # Parse JSON
        from app import app  # 🚀 Lazy import untuk menghindari circular import

        with app.app_context():  # Gunakan app hanya di sini
            new_data = SensorData(
    temperature=data_json.get("temperature"),
    humidity=data_json.get("humidity"),
    mq_status=data_json.get("MQ"),  # ✅ Sesuai dengan nama kolom di PostgreSQL
    flame_status=data_json.get("Flame")  # ✅ Sesuai dengan nama kolom di PostgreSQL
)
            db.session.add(new_data)
            db.session.commit()
            print("✅ Data successfully saved to database!")
    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")

def start_mqtt():
    client = mqtt.Client(client_id=Config.MQTT_CLIENT_ID)

    # Menambahkan autentikasi username & password
    client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)

    # **PENTING:** Menambahkan TLS/SSL agar bisa konek ke port 8883
    client.tls_set(cert_reqs=ssl.CERT_NONE)  # Nonaktifkan verifikasi sertifikat
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("🔗 Connecting to MQTT Broker...")
        client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, 60)
        print("✅ Successfully connected!")
        client.loop_start()  # Penting: biar client tetap berjalan!
    except Exception as e:
        print(f"❌ Failed to connect: {e}")