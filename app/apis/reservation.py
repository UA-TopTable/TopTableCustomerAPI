import uuid
from flask import Blueprint, render_template, request
from flask_restx import Namespace, Resource,fields
from sqlalchemy.exc import IntegrityError
from services.db_service import add_reservation, get_reservation
from datetime import datetime

api=Namespace("reservation",description="Operations for reservations")

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
        
        time_slot = data.get('reservation_time_slot')
        reservation_date = data.get('reservation_date')
        if not time_slot or not reservation_date:
            return 'Reservation date and slot is required', 400
        else:
            try:
                start_hour, end_hour = time_slot.split('-')
                start_time_str = f"{reservation_date} {start_hour}"
                end_time_str = f"{reservation_date} {end_hour}"
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
                end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
            except ValueError:
                return 'Invalid date format', 400
            data['reservation_start_time'] = start_time
            data['reservation_end_time'] = end_time

        if 'reservation_code' not in data:
            data['reservation_code'] = str(uuid.uuid4())[:6]

        required_fields = [
            'user_id', 'restaurant_id', 'dining_table_id', 'number_of_people',
            'reservation_start_time', 'reservation_end_time', 'reservation_code'
        ]

        if not all(field in data for field in required_fields):
            print(data)
            return 'Missing required fields', 400
        try:
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
                return 'Table not found', 404
            return result.get('id'), 201
        except IntegrityError as e:
            print(e)
            return f'Invalid request', 400

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
            
