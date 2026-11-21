const BASE_URL = `${location.protocol}//${location.hostname}:8000/api`;

async function request(path, method = "GET", data, expectList = false) {
  const headers = { Accept: "application/json" };
  const options = { method, headers };
  if (data !== undefined) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(data);
  }

  let res;
  try {
    res = await fetch(BASE_URL + path, options);
  } catch {
    throw new Error("No se pudo conectar con el servidor. Comprueba la conexión.");
  }
  if (res.ok && res.status === 204) return null;

  let body;
  try {
    body = await res.json();
  } catch {
    throw new Error(`El servidor devolvió una respuesta inesperada (HTTP ${res.status}).`);
  }
  if (!res.ok) {
    throw new Error(typeof body?.error === "string" && body.error.trim()
      ? body.error : `No se pudo completar la operación (HTTP ${res.status}).`);
  }
  if (body === null || typeof body !== "object" || Array.isArray(body) !== expectList) {
    throw new Error("El servidor devolvió datos con un formato inesperado.");
  }
  return body;
}

function list(path, filters = {}) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value != null && value !== "") params.set(key, value);
  }
  return request(params.size ? path + "?" + params : path, "GET", undefined, true);
}

export const listRooms = (status) => list("/rooms", { status });
export const getRoom = (id) => request(`/rooms/${id}`);
export const createRoom = (data) => request("/rooms", "POST", data);
export const updateRoom = (id, data) => request(`/rooms/${id}`, "PUT", data);
export const deleteRoom = (id) => request(`/rooms/${id}`, "DELETE");

export const listGuests = () => list("/guests");
export const getGuest = (id) => request(`/guests/${id}`);
export const createGuest = (data) => request("/guests", "POST", data);
export const deleteGuest = (id) => request(`/guests/${id}`, "DELETE");

export const listReservations = (status, guestId) => list("/reservations", { status, guest_id: guestId });
export const getReservation = (id) => request(`/reservations/${id}`);
export const createReservation = (data) => request("/reservations", "POST", data);
export const cancelReservation = (id) => request(`/reservations/${id}/cancel`, "PATCH");
export const checkInReservation = (id) => request(`/reservations/${id}/check-in`, "PATCH");
export const checkOutReservation = (id) => request(`/reservations/${id}/check-out`, "PATCH");
