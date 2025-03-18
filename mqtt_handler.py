import paho.mqtt.client as mqtt
import ssl
import json
from models import SensorData
from database import db

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Successfully connected to MQTT Broker!")
        client.subscribe("fire_detector/data")  # Subscribe ke topik
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

    try:
        data_json = json.loads(msg.payload.decode())  # Parse JSON
        temperature = data_json.get("temperature")
        humidity = data_json.get("humidity")
        mq_status = data_json.get("MQ") 
        flame_status = data_json.get("Flame")

        if temperature is None or humidity is None:
            print("⚠️ Invalid data: Temperature or humidity is None. Data ignored.")
            return  # Abaikan penyimpanan jika data tidak valid

        new_data = SensorData(
            temperature=temperature,
            humidity=humidity,
            mq_status=mq_status,
            flame_status=flame_status
        )
        db.session.add(new_data)
        db.session.commit()
        print("✅ Data successfully saved to database!")
    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")

def start_mqtt():
    client = mqtt.Client(client_id="Flask_Server")

    # Menambahkan autentikasi username & password
    client.username_pw_set("firedetect", "123")

    # **PENTING:** Menambahkan TLS/SSL agar bisa konek ke port 8883
    client.tls_set(cert_reqs=ssl.CERT_NONE) 
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("🔗 Connecting to MQTT Broker...")
        client.connect("d7d8ee83.ala.asia-southeast1.emqxsl.com", 8883, 60)
        print("✅ Successfully connected!")
        client.loop_start()  # Penting: biar client tetap berjalan!
    except Exception as e:
        print(f"❌ Failed to connect: {e}")