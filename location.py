from flask import Blueprint, request, jsonify
from models import db, DeviceLocation
from middleware import token_required

locations_bp = Blueprint('locations', __name__)

@locations_bp.route('/api/devices/locations', methods=['GET'])
@token_required
def get_device_locations(current_user):
    try:
        devices = DeviceLocation.query.filter_by(user_id=current_user.id).order_by(DeviceLocation.device_number).all()
        
        return jsonify([{
            "id": d.id,
            "device_number": d.device_number,
            "zone_name": d.zone_name,
            "device_location": d.device_location,
            "created_at": d.created_at.isoformat(),
            "updated_at": d.updated_at.isoformat()
        } for d in devices])
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint POST untuk update/create data
@locations_bp.route('/api/devices/locations/update', methods=['POST'])
@token_required
def update_device_locations(current_user):
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({"error": "Data harus berupa array"}), 400

    try:
        for device_data in data:
            # Validasi device_number
            if 'device_number' not in device_data:
                return jsonify({"error": "Device number harus disertakan"}), 400
            
            device = DeviceLocation.query.filter_by(
                user_id=current_user.id,
                device_number=device_data['device_number']
            ).first()

            if not device:
                device = DeviceLocation(
                    user_id=current_user.id,
                    device_number=device_data['device_number']
                )
                db.session.add(device)

            # Update data
            if 'zone_name' in device_data:
                device.zone_name = device_data['zone_name']
            
            if 'device_location' in device_data:
                # Validasi format
                if not isinstance(device_data['device_location'], str) or device_data['device_location'].count(',') != 1:
                    return jsonify({"error": "Format lokasi harus 'latitude,longitude'"}), 400
                device.device_location = device_data['device_location']

        db.session.commit()
        return jsonify({
            "message": "Lokasi perangkat berhasil diperbarui",
            "updated_devices": len(data)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Gagal memperbarui data: {str(e)}"}), 500