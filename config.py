import os

class Config:
    MQTT_BROKER = "d7d8ee83.ala.asia-southeast1.emqxsl.com"
    MQTT_PORT = 8883
    MQTT_TOPIC = "fire_detector/data"
    MQTT_CLIENT_ID = "Flask_Server"
    MQTT_USERNAME = "firedetect"
    MQTT_PASSWORD = "123"

    # Konfigurasi Database PostgreSQL (ubah jika pakai layanan lain)
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:123@localhost:5432/iot_database"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
