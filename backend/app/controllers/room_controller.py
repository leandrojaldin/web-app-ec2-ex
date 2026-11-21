
from flask import Blueprint, jsonify, request

from ..services import rooms
from ..views.room_view import room_to_dict, rooms_to_list

room_bp = Blueprint("rooms", __name__, url_prefix="/api/rooms")


@room_bp.get("")
def list_rooms():
    return jsonify(rooms_to_list(rooms.list_rooms(request.args.get("status"))))


@room_bp.get("/<int:room_id>")
def get_room(room_id):
    return jsonify(room_to_dict(rooms.get_room(room_id)))


@room_bp.post("")
def create_room():
    room = rooms.create_room(request.get_json(silent=True) or {})
    return jsonify(room_to_dict(room)), 201


@room_bp.put("/<int:room_id>")
def update_room(room_id):
    room = rooms.update_room(room_id, request.get_json(silent=True) or {})
    return jsonify(room_to_dict(room))


@room_bp.delete("/<int:room_id>")
def delete_room(room_id):
    rooms.delete_room(room_id)
    return "", 204
