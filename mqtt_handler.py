import paho.mqtt.client as mqtt
import ssl
import json
from database import db

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Successfully connected to MQTT Broker!")
        client.subscribe("fire_detector/#")
    else:
        print(f"❌ Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    from app import app 
    from models import RuangTamuData, KamarData, db

    print(f"📥 Topic: {msg.topic} | Payload: {msg.payload.decode()}")

    try:
        data_json = json.loads(msg.payload.decode())
        temperature = data_json.get("temperature")
        humidity = data_json.get("humidity")
        mq_status = data_json.get("MQ")
        flame_status = data_json.get("Flame")

        if temperature is None or humidity is None:
            print("⚠️ Data tidak lengkap. Data diabaikan.")
            return

        with app.app_context():
            if msg.topic == "fire_detector/data":
                new_data = RuangTamuData(
                    temperature=temperature,
                    humidity=humidity,
                    mq_status=mq_status,
                    flame_status=flame_status
                )
                db.session.add(new_data)
                db.session.commit()
                print("✅ Data berhasil disimpan ke tabel: ruang_tamu")

            elif msg.topic == "fire_detector/data2":
                new_data = KamarData(
                    temperature=temperature,
                    humidity=humidity,
                    mq_status=mq_status,
                    flame_status=flame_status
                )
                db.session.add(new_data)
                db.session.commit()
                print("✅ Data berhasil disimpan ke tabel: kamar")

            else:
                print(f"⚠️ Topik tidak dikenali: {msg.topic}. Data diabaikan.")

    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")


def start_mqtt():
    client = mqtt.Client(client_id="Flask_Server")

    client.username_pw_set("firedetect", "123")
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("🔗 Connecting to MQTT Broker...")
        client.connect("d7d8ee83.ala.asia-southeast1.emqxsl.com", 8883, 60)
        print("✅ Successfully connected!")
        client.loop_start()
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
