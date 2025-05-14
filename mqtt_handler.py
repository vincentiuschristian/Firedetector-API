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
    from models import RuangTamuData, KamarData, User, db

    print(f"📥 Topic: {msg.topic} | Payload: {msg.payload.decode()}")

    try:
        data_json = json.loads(msg.payload.decode())
        
        with app.app_context():
            # Dapatkan user default (misalnya user pertama)
            default_user = User.query.first()
            if not default_user:
                print("⚠️ No users found in database!")
                return

            if msg.topic == "fire_detector/data":
                new_data = RuangTamuData(
                    user_id=default_user.id,  # Selalu sertakan user_id
                    temperature=data_json.get("temperature"),
                    humidity=data_json.get("humidity"),
                    mq_status=data_json.get("MQ"),
                    flame_status=data_json.get("Flame")
                )
                db.session.add(new_data)
                db.session.commit()
                print(f"✅ Data saved to ruang_tamu for user {default_user.id}")

            elif msg.topic == "fire_detector/data2":
                new_data = KamarData(
                    user_id=default_user.id,
                    temperature=data_json.get("temperature"),
                    humidity=data_json.get("humidity"),
                    mq_status=data_json.get("MQ"),
                    flame_status=data_json.get("Flame")
                )
                db.session.add(new_data)
                db.session.commit()
                print(f"✅ Data saved to kamar for user {default_user.id}")

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
