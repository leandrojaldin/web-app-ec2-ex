
from datetime import datetime, timedelta, timezone

import pytest


@pytest.fixture
def booking(client, room, guest):
    start = datetime.now(timezone(timedelta(hours=-4))).date() + timedelta(days=10)
    return {
        "room_id": room["id"],
        "guest_id": guest["id"],
        "check_in": start.isoformat(),
        "check_out": (start + timedelta(days=2)).isoformat(),
        "guests_count": 2,
    }


def assert_rule_error(response, message):
    assert response.status_code == 422
    assert response.get_json() == {"error": message}


@pytest.mark.parametrize("nights", [0, -1])
def test_departure_must_follow_arrival(client, booking, nights):
    start = datetime.fromisoformat(booking["check_in"]).date()
    booking["check_out"] = (start + timedelta(days=nights)).isoformat()
    response = client.post("/api/reservations", json=booking)
    assert_rule_error(response, "La fecha de salida debe ser posterior a la de ingreso")


def test_arrival_cannot_be_in_the_past(client, booking):
    yesterday = datetime.now(timezone(timedelta(hours=-4))).date() - timedelta(days=1)
    booking["check_in"] = yesterday.isoformat()
    response = client.post("/api/reservations", json=booking)
    assert_rule_error(response, "La fecha de ingreso no puede estar en el pasado")


def test_same_room_overlap_is_rejected(client, booking):
    assert client.post("/api/reservations", json=booking).status_code == 201
    response = client.post("/api/reservations", json=booking)
    assert_rule_error(response, "La habitación ya está reservada en esas fechas")


def test_departure_and_next_arrival_can_share_a_date(client, booking):
    assert client.post("/api/reservations", json=booking).status_code == 201
    next_arrival = datetime.fromisoformat(booking["check_out"]).date()
    booking["check_in"] = next_arrival.isoformat()
    booking["check_out"] = (next_arrival + timedelta(days=1)).isoformat()
    assert client.post("/api/reservations", json=booking).status_code == 201


def test_cancelled_reservation_does_not_block_dates(client, booking):
    created = client.post("/api/reservations", json=booking)
    assert created.status_code == 201
    reservation_id = created.get_json()["id"]
    assert client.patch(f"/api/reservations/{reservation_id}/cancel").status_code == 200
    assert client.post("/api/reservations", json=booking).status_code == 201


@pytest.mark.parametrize("guests_count", [0, 3])
def test_guest_count_must_fit_room_capacity(client, booking, guests_count):
    booking["guests_count"] = guests_count
    response = client.post("/api/reservations", json=booking)
    assert_rule_error(response, "La cantidad de huéspedes debe estar entre 1 y 2")


def test_maintenance_room_cannot_be_booked(client, booking):
    room_id = booking["room_id"]
    assert client.put(f"/api/rooms/{room_id}", json={"status": "maintenance"}).status_code == 200
    response = client.post("/api/reservations", json=booking)
    assert_rule_error(response, "La habitación está en mantenimiento")


@pytest.mark.parametrize(("nights", "expected_total"), [(6, 1800), (7, 1890), (8, 2160)])
def test_discount_starts_at_seven_nights(client, booking, nights, expected_total):
    start = datetime.fromisoformat(booking["check_in"]).date()
    booking["check_out"] = (start + timedelta(days=nights)).isoformat()
    response = client.post("/api/reservations", json=booking)
    assert response.status_code == 201
    assert response.get_json()["nights"] == nights
    assert response.get_json()["total_price"] == expected_total
