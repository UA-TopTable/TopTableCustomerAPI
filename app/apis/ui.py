import sys
import boto3
from urllib.parse import urlparse
from flask import make_response, redirect, render_template, request
from flask_restx import Namespace,Resource
from services.db_service import get_reservation, get_restaurant, get_all_restaurants, get_pictures, get_all_tables,get_table_by_id,get_user_by_id,get_user_reservations,get_restaurant_by_id
from services.auth_service import get_user

api=Namespace("ui",path="/ui",description="UI-related endpoints")

@api.route("/restaurant/<int:id>")
class RestaurantPage(Resource):
    def get(self, id):
        tables = get_all_tables(id)
        restaurant = get_restaurant(id)
        if restaurant is None:
            return make_response("No restaurant found", 404)
        if tables is None:
            return make_response("No tables for this restaurant", 404)
        else:
            return make_response(
                render_template("restaurant.html", restaurant=restaurant, tables=tables),
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
    

@api.route("/homes")
class HomePage(Resource):
    def get(self):
        print("home")
        restaurants = get_all_restaurants()
        try:
            for restaurant in restaurants :
                if restaurant['restaurant_image'] != '' and not(restaurant['restaurant_image'] is None) :
                    parsed_url = urlparse(restaurant['restaurant_image'])
                    
                    bucket_name = parsed_url.netloc.split('.')[0]
                    object_key = parsed_url.path.lstrip('/')
                    s3_client = boto3.client('s3')
                    signed_url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': bucket_name, 'Key': object_key},
                            ExpiresIn=3600  # Expiration en secondes (ici, 1 heure par défaut)
                    )
                    restaurant['restaurant_image'] = signed_url
        except Exception as e:
            for restaurant in restaurants:
                restaurant['restaurant_image'] = ''
            print(e)

        return make_response(
            render_template("index.html", restaurants=restaurants),
            200,
            {'Content-Type': 'text/html'}
        )
    

@api.route("/book_restaurant/<int:id>")
class BookRestaurantPage(Resource):
    def get(self, id):
        restaurant = get_restaurant(id)
        try:
            pictures = get_pictures(id)
            if not (pictures == [] or pictures is None): 
                parsed_url = urlparse(pictures[0]['link'])
                
                bucket_name = parsed_url.netloc.split('.')[0]
                object_key = parsed_url.path.lstrip('/')
                s3_client = boto3.client('s3')
                signed_url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket_name, 'Key': object_key},
                        ExpiresIn=3600  # Expiration en secondes (ici, 1 heure par défaut)
                )
                print(signed_url)
                pictures[0]['link'] = signed_url
            # pictures = pictures if pictures is not None else []
            #TODO: check if we correctly get the user
            #access_token=request.cookies.get("access_token")
            #user = get_user(access_token)
        except Exception as e:
            print(e)
        # class tmpUser:
        #     id=4
        # user=tmpUser()
        access_token=request.cookies.get("access_token")
        user = get_user(access_token)
        return make_response(
            render_template("book_restaurant.html", restaurant=restaurant, pictures=pictures, user=user),
            200,
            {'Content-Type': 'text/html'}
        )
    
    
@api.route("/user/reservations",endpoint="user_reservations_page")
class UserReservationsPage(Resource):
    @api.param("starts_after", "Filter reservations that start after date")
    @api.param("ends_before", "Filter reservations that end before date")
    @api.param("restaurant_id", "Filter reservations that belong to a specific restaurant")
    def get(self):
        if 'x-amzn-oidc-accesstoken' in request.headers:
            access_token = request.headers.get('x-amzn-oidc-accesstoken')
        elif "access_token" in request.cookies:
            access_token=request.cookies.get("access_token")
        else:
            return redirect("/auth/login")
        
        if(access_token is None):
            return "no access token",400
        user=get_user(access_token)

        starts_after=None
        ends_before=None
        restaurant_id=None

        if "starts_after" in request.args and request.args.get("starts_after")!="":
            starts_after=request.args.get("starts_after")
        
        if "ends_before" in request.args and request.args.get("ends_before")!="":
            ends_before=request.args.get("ends_before")
        
        if "restaurant_id" in request.args and request.args.get("restaurant_id")!="":
            restaurant_id=request.args.get("restaurant_id")

        reservations_raw=get_user_reservations(user["id"],starts_after=starts_after,ends_before=ends_before,restaurant_id=restaurant_id)

        restaurants=[]

        reservations=[]
        #get table number and customer name to make it more human-readable
        for reservation in reservations_raw:
            reservation=reservation.as_dict()

            table=get_table_by_id(reservation['dining_table_id'])
            reservation['table_number']=table.table_number if table is not None else ""

            restaurant=get_restaurant_by_id(reservation["restaurant_id"])
            reservation['restaurant_name']=restaurant.name if restaurant is not None else ""

            reservations.append(reservation)
            restaurants.append((reservation["restaurant_id"],reservation["restaurant_name"]))

        return make_response(
            render_template("reservations.html", reservations=reservations,restaurants=restaurants),
            200,
            {'Content-Type': 'text/html'}
        )