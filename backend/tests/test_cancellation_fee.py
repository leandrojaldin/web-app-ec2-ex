
from datetime import datetime, timedelta

import pytest

from app.models import ReservationRate, db
from app.services import reservations


def book_week(client, room, guest, monkeypatch):
    arrival = datetime(2030, 6, 19, tzinfo=reservations.HOTEL_TIMEZONE)
    monkeypatch.setattr(reservations, "hotel_now", lambda: arrival - timedelta(days=3))
    response = client.post("/api/reservations", json={
        "room_id": room["id"],
        "guest_id": guest["id"],
        "check_in": arrival.date().isoformat(),
        "check_out": (arrival.date() + timedelta(days=7)).isoformat(),
        "guests_count": 1,
    })
    assert response.status_code == 201
    assert response.get_json()["total_price"] == 1890
    return response.get_json()["id"], arrival


@pytest.mark.parametrize(("seconds_before", "expected_fee"), [(172800, 0), (172799, 300)])
def test_cancellation_fee_uses_strict_48_hour_limit(client, room, guest, monkeypatch, seconds_before, expected_fee):
    reservation_id, arrival = book_week(client, room, guest, monkeypatch)
    room_id = room["id"]
    assert client.put(f"/api/rooms/{room_id}", json={"price_per_night": 450}).status_code == 200

    monkeypatch.setattr(reservations, "hotel_now", lambda: arrival - timedelta(seconds=seconds_before))
    response = client.patch(f"/api/reservations/{reservation_id}/cancel")
    assert response.status_code == 200
    assert response.get_json()["status"] == "cancelled"
    assert response.get_json()["total_price"] == expected_fee
    assert client.get(f"/api/reservations/{reservation_id}").get_json()["total_price"] == expected_fee


def test_legacy_reservation_uses_rate_from_original_total(app, client, room, guest, monkeypatch):
    reservation_id, arrival = book_week(client, room, guest, monkeypatch)
    with app.app_context():
        rate = db.session.get(ReservationRate, reservation_id)
        rate.reservation.total_price = 2100
        db.session.delete(rate)
        db.session.commit()

    monkeypatch.setattr(reservations, "hotel_now", lambda: arrival - timedelta(hours=1))
    response = client.patch(f"/api/reservations/{reservation_id}/cancel")
    assert response.status_code == 200
    assert response.get_json()["total_price"] == 300
