
# Reglas de negocio del Hotel Mirador

Las solicitudes que violan una regla devuelven HTTP 422 con el cuerpo JSON indicado en la tabla. Las fechas se evalúan en la hora de Bolivia.

| Regla | Condición | Respuesta |
| --- | --- | --- |
| Fechas de estadía | Al crear una reserva, la salida debe ser posterior al ingreso y el ingreso debe ser hoy o posterior. | `{"error":"La fecha de salida debe ser posterior a la de ingreso"}` o `{"error":"La fecha de ingreso no puede estar en el pasado"}`. |
| Disponibilidad por fechas | Al crear una reserva, la habitación no puede tener otra confirmada o con check-in cuyo intervalo se superponga. Salida e ingreso el mismo día son compatibles. | `{"error":"La habitación ya está reservada en esas fechas"}`. |
| Capacidad | Al crear una reserva, se exige una cantidad entera de huéspedes entre 1 y la capacidad de la habitación. | `{"error":"La cantidad de huéspedes debe estar entre 1 y N"}`, con la capacidad real, o `{"error":"La cantidad de huéspedes debe ser un número entero"}` si se recibe un número fraccionario o un booleano. |
| Mantenimiento | Al crear una reserva, se rechaza una habitación en estado `maintenance`. | `{"error":"La habitación está en mantenimiento"}`. |
| Descuento por estadía larga | Al crear una reserva de siete noches o más, se descuenta el 10 % sobre el precio por noche multiplicado por el número de noches. | Sin error. El HTTP 201 incluye el importe final en `total_price`. |

Reglas adicionales identificadas en el relato de Lucía:

| Regla | Condición | Respuesta prevista |
| --- | --- | --- |
| Penalización por cancelación | Al cancelar, si quedan menos de 48 horas para la fecha de ingreso, se cobra la primera noche. Si quedan 48 horas o más, no hay cargo. | Sin error. El HTTP 200 incluye la penalidad o cero en `total_price`. |
| Transiciones de estado | Una reserva confirmada se puede cancelar o pasar a hospedada. Una reserva hospedada puede pasar a finalizada. Cancelada y finalizada son estados terminales. | HTTP 422 con `{"error":"No se permite esta acción para el estado de la reserva"}`. |
| Check-in anticipado | Al registrar un ingreso, la fecha actual debe ser igual o posterior a la fecha de ingreso de la reserva. | HTTP 422 con `{"error":"El check-in no puede realizarse antes de la fecha de ingreso"}`. |
| Límite por huésped | Al crear una reserva, el huésped debe tener menos de tres reservas activas, contando las confirmadas y las que tienen check-in. | HTTP 422 con `{"error":"El huésped ya tiene tres reservas activas"}`. |

Los errores de formato o campos obligatorios conservan HTTP 400. Los registros inexistentes y duplicados conservan sus códigos HTTP 404 y 409, respectivamente.
