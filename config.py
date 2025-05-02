import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MQTT_BROKER = "d7d8ee83.ala.asia-southeast1.emqxsl.com"
    MQTT_PORT = 8883
    MQTT_TOPIC = "fire_detector/#"
    MQTT_CLIENT_ID = "Flask_Server"
    MQTT_USERNAME = "firedetect"
    MQTT_PASSWORD = "123"

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:123@localhost:5432/iot_database")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
