import sys
from flask import request
from flask_restx import Namespace, Resource,fields

from services.db_service import get_user_reservations
from services.auth_service import get_user


api=Namespace("user",path="/api/v1/user",description="User related operations")

reservation_model=api.model('Reservation', {
    "id": fields.Integer(required=True, description="The reservation id"),
    "user_id": fields.Integer(required=True, description="The user id"),
    "restaurant_id": fields.Integer(required=True, description="The restaurant id"),
    "dining_table_id": fields.Integer(required=True, description="The dining table id"),
    "number_of_people": fields.Integer(required=True, description="The number of people"),
    "reservation_start_time": fields.DateTime(required=True, description="The reservation start time"),
    "reservation_end_time": fields.DateTime(required=True, description="The reservation end time"),
    "status": fields.String(enum=['pending', 'confirmed', 'cancelled'], required=True, description="The reservation status"),
    "special_requests": fields.String(required=False, description="The special requests"),
})

@api.route("/reservations",endpoint="user_reservations")
class UserReservations(Resource):
    @api.doc("Get user reservations")
    @api.param("starts_after", "Filter reservations that start after date")
    @api.param("ends_before", "Filter reservations that end before date")
    @api.param("restaurant_id", "Filter reservations that belong to a specific restaurant")
    @api.response(200,description="reservations list",model=fields.List(fields.Nested(reservation_model)))
    @api.response(401,"unauthorized")
    def get(self):
        if 'x-amzn-oidc-accesstoken' in request.headers:
            access_token = request.headers.get('x-amzn-oidc-accesstoken')
        elif "access_token" in request.cookies:
            access_token=request.cookies.get("access_token")
        else:
            return "not authorized",401
        
        user=get_user(access_token)
        if user is None:
            return "unauthorized",401
        
        starts_after=None
        ends_before=None
        restaurant_id=None

        if "starts_after" in request.args:
            starts_after=request.args.get("starts_after")
        
        if "ends_before" in request.args:
            ends_before=request.args.get("ends_before")
        
        if "restaurant_id" in request.args:
            restaurant_id=request.args.get("restaurant_id")
        
        reservations=get_user_reservations(user["id"],starts_after,ends_before,restaurant_id)

        return [reservation.as_dict() for reservation in reservations],200
