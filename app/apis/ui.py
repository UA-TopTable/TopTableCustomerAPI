import sys
from flask import make_response, render_template
from flask_restx import Namespace,Resource
from services.db_service import get_reservation, get_restaurant

api=Namespace("ui",description="UI-related endpoints")

@api.route("/restaurant/<int:id>")
class RestaurantPage(Resource):
    def get(self, id):
        restaurant = get_restaurant(id)
        if restaurant is None:
            return make_response("Restaurant not found", 404)
        else:
            return make_response(
                render_template("restaurant.html", restaurant=restaurant),
                200,
                {'Content-Type': 'text/html'}
            )
        
@api.route("/reservation/<int:id>")
class ReservationPage(Resource):
    def get(self, id):
        reservation = get_reservation(id)
        if reservation is None:
            return make_response("Reservation not found", 404)
        else:
            return make_response(
                render_template("reservation.html", reservation=reservation),
                200,
                {'Content-Type': 'text/html'}
            )

@api.route("/reservation")
class ReservationPage(Resource):
    def get(self):
        return make_response(
            render_template("new_reservation.html"),
            200,
            {'Content-Type': 'text/html'}
        )

@api.route("/auth/confirm")
class ConfirmRegistration(Resource):
    def get(self):
        return make_response(
            render_template("confirmRegistration.html"),
            200,
            {'Content-Type':'text/html'}
        )