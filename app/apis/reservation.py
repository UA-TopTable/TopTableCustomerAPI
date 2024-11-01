from flask import Blueprint, render_template, request
from flask_restx import Namespace, Resource,fields
import sqlalchemy
from services.db_service import add_reservation, get_reservation

api=Namespace("reservation",description="Operations for managing the Reservation")

@api.route('/')
class Reservation(Resource):
    @api.doc("Create a new Reservation")
    @api.expect({
        "user_id": fields.String(required=True),
        "restaurant_id": fields.String(required=True),
        "dining_table_id": fields.String(required=True),
        "number_of_people": fields.Integer(required=True),
        "reservation_start_time": fields.String(required=True),
        "reservation_end_time": fields.String(required=True),
        "status": fields.String(required=True),
        "special_requests": fields.String(required=False),
        "reservation_code": fields.String(required=True)
    })
    @api.response(201, "Reservation saved")
    @api.response(400, "Missing required fields")
    def post(self):
        data = request.json
        if not data:
            return 'Body is required', 400

        required_fields = [
            'user_id', 'restaurant_id', 'dining_table_id', 'number_of_people',
            'reservation_start_time', 'reservation_end_time', 'status', 'reservation_code'
        ]

        if not all(field in data for field in required_fields):
            return 'Missing required fields', 400
        try:
            result = add_reservation(
                user_id=data['user_id'],
                restaurant_id=data['restaurant_id'],
                dining_table_id=data['dining_table_id'],
                number_of_people=data['number_of_people'],
                reservation_start_time=data['reservation_start_time'],
                reservation_end_time=data['reservation_end_time'],
                status=data['status'],
                special_requests=data.get('special_requests'),
                reservation_code=data['reservation_code']
            )
            if not result:
                return 'Table not found', 404
            return result, 200
        except sqlalchemy.exc.IntegrityError as e:
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
            
