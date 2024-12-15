import boto3
from urllib.parse import urlparse
from flask import make_response, redirect, render_template, request
from flask_restx import Namespace,Resource
from services.db_service import get_all_restaurants_filtered, get_reservation, get_restaurant, get_all_restaurants, get_pictures, get_all_tables,get_table_by_id,get_user_reservations,get_restaurant_by_id
from services.auth_service import get_user

api=Namespace("ui",path="/ui",description="UI-related endpoints")

@api.route("/restaurant/<int:id>")
class RestaurantPage(Resource):
    def get(self, id):
        if 'x-amzn-oidc-accesstoken' in request.headers:
            access_token = request.headers.get('x-amzn-oidc-accesstoken')
        elif "access_token" in request.cookies:
            access_token=request.cookies.get("access_token")
        else:
            return "not authorized",401
        user = get_user(access_token)

        tables = get_all_tables(id)
        restaurant = get_restaurant(id)
        if restaurant is None:
            return make_response("No restaurant found", 404)
        if tables is None:
            return make_response("No tables for this restaurant", 404)
        else:
            return make_response(
                render_template("restaurant.html", restaurant=restaurant, tables=tables, user=user),
                200,
                {'Content-Type': 'text/html'}
            )
        
@api.route("/reservation/<int:id>")
class ReservationPage(Resource):
    def get(self, id):
        if 'x-amzn-oidc-accesstoken' in request.headers:
            access_token = request.headers.get('x-amzn-oidc-accesstoken')
        elif "access_token" in request.cookies:
            access_token=request.cookies.get("access_token")
        else:
            return "not authorized",401
        user = get_user(access_token)

        reservation = get_reservation(id)
        if reservation is None:
            return make_response("Reservation not found", 404)
        else:
            return make_response(
                render_template("reservation.html", reservation=reservation, user=user),
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
        # if 'x-amzn-oidc-accesstoken' in request.headers:
        #     access_token = request.headers.get('x-amzn-oidc-accesstoken')
        # elif "access_token" in request.cookies:
        #     access_token=request.cookies.get("access_token")
        # else:
        #     return "not authorized",401
        # user = get_user(access_token)
        user = {
            "full_name": "Test User",
            "email": "fdsaf"
        }

        query = request.args.get('query', '')
        category = request.args.get('category', '')
        if query or category:
            restaurants = get_all_restaurants_filtered(query,category)
        else:
            restaurants = get_all_restaurants()
        try:
            for r in restaurants:
                pictures = get_pictures(r['id'])
                if not (pictures == [] or pictures is None):
                    picture = pictures[0]
                    parsed_url = urlparse(picture['link'])
                    
                    bucket_name = parsed_url.netloc.split('.')[0]
                    object_key = parsed_url.path.lstrip('/')
                    s3_client = boto3.client('s3')
                    signed_url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': bucket_name, 'Key': object_key},
                            ExpiresIn=3600 
                    )
                    print(signed_url)
                    r['restaurant_image'] = signed_url
            
        except Exception as e:
            print(e)

        return make_response(
            render_template("index.html", restaurants=restaurants, user=user),
            200,
            {'Content-Type': 'text/html'}
        )
    

@api.route("/book_restaurant/<int:id>")
class BookRestaurantPage(Resource):
    def get(self, id):
        restaurant = get_restaurant(id)
        pictures = get_pictures(id)
        try:
            if not (pictures == [] or pictures is None):
                for picture in pictures : 
                    parsed_url = urlparse(picture['link'])
                    
                    bucket_name = parsed_url.netloc.split('.')[0]
                    object_key = parsed_url.path.lstrip('/')
                    s3_client = boto3.client('s3')
                    signed_url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': bucket_name, 'Key': object_key},
                            ExpiresIn=3600 
                    )
                    print(signed_url)
                    picture['link'] = signed_url
        except Exception as e:
            print(e)
        
        if 'x-amzn-oidc-accesstoken' in request.headers:
            access_token = request.headers.get('x-amzn-oidc-accesstoken')
        elif "access_token" in request.cookies:
            access_token=request.cookies.get("access_token")
        else:
            return "not authorized",401
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
        user = {
            "full_name": "Test User",
            "email": "fdsaf",
            "id": "123"
        }

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

        reservations.sort(key=lambda x: x['reservation_start_time'],reverse=True)

        return make_response(
            render_template("reservations.html", reservations=reservations,restaurants=restaurants, user=user),
            200,
            {'Content-Type': 'text/html'}
        )
    

from services.db_service import add_restaurant, add_table, add_working_hours, delete_all_data, add_reservation, save_user_account
from datetime import datetime
@api.route("/mock_data")
class MockDataPage(Resource):
    def get(self):
        try:
            user_id = 1
            restaurant_data = {
            "name": "Restaurant Test",
            "description": "Restaurant Test",
            "location_address": "Address 1",
            "location_latitude": "1",
            "location_longitude": "1",
            "restaurant_image": "https://toptable-bucket.s3.us-east-1.amazonaws.com/restaurant1.png",
            "time_zone": "UTC",
            "owner_user_id": user_id
            }
            restaurant =  add_restaurant(restaurant_data)
            restr_id = restaurant.get('id')
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for day in days_of_week:
                add_working_hours(restaurant_id=restr_id, day_of_week=day, opening_time="09:00", closing_time="21:00")
            table1 = add_table(table_number="1",restaurant_id=restr_id,number_of_seats=4, table_type="indoor", description="Table 1")
            table2 = add_table(table_number="2",restaurant_id=restr_id,number_of_seats=4, table_type="indoor", description="Table 2")
            table_id = table1.get('id')
            reservation_start_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
            reservation_end_time = reservation_start_time.replace(hour=10, minute=30)
            reservation_code = str(int(datetime.timestamp(datetime.now())))[-10:]
            add_reservation(user_id=user_id, restaurant_id=restr_id, dining_table_id=table_id, number_of_people=4, reservation_code=reservation_code,
                            reservation_start_time=reservation_start_time, reservation_end_time=reservation_end_time)
            
            return "Mock data created successfully", 200
        except Exception as e:
            return e