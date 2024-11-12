import sys
import uuid
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from util.utils import parse_time_slot
from services.db_service import add_reservation, get_reservation, delete_reservation

api=Namespace("reservation", path="/api/v1/reservation", description="Operations for reservations")

@api.route('/')
class Reservation(Resource):
    @api.doc("Create a new Reservation")
    @api.expect(api.model('Reservation', {
        "user_id": fields.String(required=True),
        "restaurant_id": fields.String(required=True),
        "dining_table_id": fields.String(required=True),
        "number_of_people": fields.Integer(required=True),
        "reservation_date": fields.String(required=True),
        "reservation_time_slot": fields.String(required=True),
        "special_requests": fields.String(required=False),
    }))
    @api.response(201, "Reservation saved")
    @api.response(400, "Missing required fields")
    def post(self):
        data = request.json
        if not data:
            return 'Body is required', 400
        
        required_fields = [
            'user_id', 'restaurant_id', 'dining_table_id', 'number_of_people',
            'reservation_date', 'reservation_time_slot'
        ]

        if not all(field in data for field in required_fields):
            return 'Missing required fields', 400
        
        try:
            time_slot = data.get('reservation_time_slot')
            reservation_date = data.get('reservation_date')
            start_time, end_time = parse_time_slot(reservation_date, time_slot)
            data['reservation_start_time'] = start_time
            data['reservation_end_time'] = end_time
        except ValueError:
            return 'Invalid date/time slot format', 400


        try:
            data['reservation_code'] = str(uuid.uuid4())[:6]
            result = add_reservation(
                user_id=data['user_id'],
                restaurant_id=data['restaurant_id'],
                dining_table_id=data['dining_table_id'],
                number_of_people=data['number_of_people'],
                reservation_start_time=data['reservation_start_time'],
                reservation_end_time=data['reservation_end_time'],
                special_requests=data.get('special_requests'),
                reservation_code=data['reservation_code']
            )
            if not result:
                return 'Table not found or request parameters are invalid', 400
            return result.get('id'), 201
        except IntegrityError as e:
            return 'Invalid request', 400

@api.route('/<int:reservation_id>')
class ReservationById(Resource):
    @api.doc("Get a reservation by id")
    @api.response(200, "Reservation found")
    @api.response(404, "Reservation not found")
    def get(self, reservation_id):
        try:
            result = get_reservation(reservation_id)
            if not result:
                return 'Reservation not found', 404
            return result, 200
        except Exception as e:
            print(e)
            return 'Invalid request', 400
            
@api.route('/deletes/<int:reservation_id>')
class ReservationDelete(Resource):
    @api.doc("Delete a reservation by id")
    @api.response(200, "Reservation deleted")
    @api.response(404, "Reservation not found")
    def get(self, reservation_id):
        try:
            delete_reservation(reservation_id)
            return 200
        except Exception as e:
            print(e)
            return 'Invalid request', 400