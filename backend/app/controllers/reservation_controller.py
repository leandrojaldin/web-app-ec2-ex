
from flask import Blueprint, jsonify, request

from ..services import reservations
from ..views.reservation_view import reservation_to_dict, reservations_to_list

reservation_bp = Blueprint("reservations", __name__, url_prefix="/api/reservations")


@reservation_bp.get("")
def list_reservations():
    status = request.args.get("status")
    guest_id = request.args.get("guest_id", type=int)
    return jsonify(reservations_to_list(reservations.list_reservations(status, guest_id)))


@reservation_bp.get("/<int:reservation_id>")
def get_reservation(reservation_id):
    return jsonify(reservation_to_dict(reservations.get_reservation(reservation_id)))


@reservation_bp.post("")
def create_reservation():
    reservation = reservations.create_reservation(request.get_json(silent=True) or {})
    return jsonify(reservation_to_dict(reservation)), 201


@reservation_bp.patch("/<int:reservation_id>/cancel")
def cancel_reservation(reservation_id):
    return jsonify(reservation_to_dict(reservations.cancel_reservation(reservation_id)))


@reservation_bp.patch("/<int:reservation_id>/check-in")
def check_in_reservation(reservation_id):
    return jsonify(reservation_to_dict(reservations.check_in_reservation(reservation_id)))


@reservation_bp.patch("/<int:reservation_id>/check-out")
def check_out_reservation(reservation_id):
    return jsonify(reservation_to_dict(reservations.check_out_reservation(reservation_id)))
