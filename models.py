from datetime import datetime, UTC
import jwt
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class RuangTamuData(db.Model):
    __tablename__ = 'ruang_tamu'
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    mq_status = db.Column(db.String(50))
    flame_status = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

class KamarData(db.Model):
    __tablename__ = 'kamar'
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    mq_status = db.Column(db.String(50))
    flame_status = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(500), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "username": self.username,
            "email": self.email,
            "location": self.location
        }
