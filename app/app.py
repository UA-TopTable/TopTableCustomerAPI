from datetime import datetime
import os
from flask import Flask

from apis import api
from secret import FLASK_SECRET_KEY


def create_app():
    app = Flask(__name__)
    api.init_app(app)
    app.secret_key=FLASK_SECRET_KEY
    # create_mock_datas()
    return app

from services.db_service import add_restaurant, add_table, add_working_hours, delete_all_data, add_reservation, add_user_account
def create_mock_datas():
    # delete_all_data() # Uncomment this line to delete all data
    user_data = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "phone": "1234567890",
        "profile_image_url": "http://example.com/image.jpg",
        "user_type": "customer",
        "password_hash": "passwordhsh"
    }
    user = add_user_account(user_data)
    user_id = user.get('id')
    print('user id', user_id)
    restaurant_data = {
        "name": "Restaurant Test",
        "description": "Restaurant Test",
        "location_address": "Address 1",
        "location_latitude": "1",
        "location_longitude": "1",
        "restaurant_image": "image1",
        "time_zone": "UTC",
        "owner_user_id": user_id
    }
    restaurant =  add_restaurant(restaurant_data)
    restr_id = restaurant.get('id')
    print('restaurant id', restr_id)
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days_of_week:
        add_working_hours(restaurant_id=restr_id, day_of_week=day, opening_time="09:00", closing_time="21:00")
    table1 = add_table(table_number="1",restaurant_id=restr_id,number_of_seats=4, table_type="indoor", description="Table 1")
    table2 = add_table(table_number="2",restaurant_id=restr_id,number_of_seats=4, table_type="indoor", description="Table 2")
    table_id = table1.get('id')
    print('table_id id', table_id)
    reservation_start_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    reservation_end_time = reservation_start_time.replace(hour=10, minute=30)
    add_reservation(user_id=user_id, restaurant_id=restr_id, dining_table_id=table_id, number_of_people=4,
                    reservation_start_time=reservation_start_time, reservation_end_time=reservation_end_time)

