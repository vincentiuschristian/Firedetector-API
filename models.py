from datetime import datetime, UTC
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from datetime import datetime
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
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(500), nullable=True)
    
    # Relasi ke DeviceLocation
    devices = db.relationship('DeviceLocation', back_populates='user', cascade='all, delete-orphan')

    # Method untuk set password
    def set_password(self, password):
        """Membuat password hash dari password plaintext"""
        self.password_hash = generate_password_hash(password, method='scrypt')

    # Method untuk verifikasi password
    def check_password(self, password):
        """Memverifikasi password terhadap hash yang tersimpan"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "username": self.username,
            "email": self.email,
            "location": self.location
        }

class DeviceLocation(db.Model):
    __tablename__ = 'device_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_number = db.Column(db.Integer, nullable=False)
    zone_name = db.Column(db.String(100), nullable=False)
    device_location = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), 
                          onupdate=lambda: datetime.now(UTC))
    
    # Relasi ke User
    user = db.relationship('User', back_populates='devices')