from flask import Blueprint, request, jsonify
from models import db, DeviceLocation
from models import DeviceLocation
from middleware import token_required_user

locations_bp = Blueprint('locations', __name__)

@locations_bp.route('/api/devices/locations', methods=['GET'])
def get_device_locations():
    @token_required_user
    def wrapped(current_user):
        try:
            devices = DeviceLocation.query.filter_by(user_id=current_user.id)\
                      .order_by(DeviceLocation.device_number).all()
            
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
    return wrapped()

@locations_bp.route('/api/devices/locations/update', methods=['POST'])
def update_device_locations():
    @token_required_user
    def wrapped(current_user):
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({"error": "Data harus berupa array"}), 400

        try:
            # ... (kode update yang sama)
            return jsonify({
                "message": "Lokasi perangkat berhasil diperbarui",
                "updated_devices": len(data)
            }), 200

        except Exception as e:
            return jsonify({"error": f"Gagal memperbarui data: {str(e)}"}), 500
    return wrapped()