from flask import Blueprint, request, jsonify
from models import db, DeviceLocation
from models import DeviceLocation
from middleware import token_required_user

locations_bp = Blueprint('locations', __name__)

@locations_bp.route('/api/devices/locations', methods=['GET'])
@token_required_user
def get_device_locations(current_user):
    try:
        devices = DeviceLocation.query.filter_by(user_id=current_user.id)\
                  .order_by(DeviceLocation.device_number).all()
        
        return jsonify([{
            "id": d.id,
            "user_id": d.user_id,
            "device_number": d.device_number,
            "zone_name": d.zone_name,
            "device_location": d.device_location,
            "created_at": d.created_at.isoformat(),
            "updated_at": d.updated_at.isoformat()
        } for d in devices])
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@locations_bp.route('/api/devices/locations/update', methods=['POST'])
@token_required_user
def update_device_locations(current_user):
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({"error": "Data must be an array"}), 400

    try:
        updated_count = 0
        for device_data in data:
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

            if 'zone_name' in device_data:
                device.zone_name = device_data['zone_name']
            
            if 'device_location' in device_data:
                device.device_location = device_data['device_location']

            updated_count += 1

        db.session.commit()
        return jsonify({
            "message": "Device locations updated successfully",
            "updated_devices": updated_count
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update data: {str(e)}"}), 500