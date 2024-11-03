import sys
import boto3
from urllib.parse import urlparse
from flask import make_response, render_template, request
from flask_restx import Namespace,Resource
from services.db_service import get_reservation, get_restaurant, get_all_restaurants, get_pictures
from services.auth_service import get_user

api=Namespace("ui",path="/ui",description="UI-related endpoints")

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
    

@api.route("/home")
class HomePage(Resource):
    def get(self):
        restaurants = get_all_restaurants()
        photos = []
        return make_response(
            render_template("index.html", restaurants=restaurants),
            200,
            {'Content-Type': 'text/html'}
        )
    

@api.route("/book_restaurant/<int:id>")
class BookRestaurantPage(Resource):
    def get(self, id):
        restaurant = get_restaurant(id)
        pictures = get_pictures(id)
        parsed_url = urlparse(pictures[0].link)
        
        bucket_name = parsed_url.netloc.split('.')[0]
        object_key = parsed_url.path.lstrip('/')
        s3_client = boto3.client('s3')
        signed_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_key},
                ExpiresIn=3600  # Expiration en secondes (ici, 1 heure par défaut)
        )
        print(signed_url)
        pictures[0].link = signed_url
        # pictures = pictures if pictures is not None else []
        #TODO: check if we correctly get the user
        #access_token=request.cookies.get("access_token")
        #user = get_user(access_token)
        class tmpUser:
            id=4
        user=tmpUser()
        return make_response(
            render_template("book_restaurant.html", restaurant=restaurant, pictures=pictures, user=user),
            200,
            {'Content-Type': 'text/html'}
        )
    
    