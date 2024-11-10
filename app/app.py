from datetime import datetime
from flask import Flask
from apis import api
from dotenv import load_dotenv
load_dotenv()

from secret import APP_PORT, FLASK_SECRET_KEY, ENV, API_URL
from flask_talisman import Talisman

def create_app():
    app = Flask(__name__)
    print("Running in ENV:", ENV)
    if ENV == "production":
        Talisman(app, force_https=True)
    app.config['API_URL'] = API_URL
    api.init_app(app)
    app.secret_key = FLASK_SECRET_KEY
    create_mock_datas(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=APP_PORT, debug=True)


from services.db_service import add_restaurant, add_table, add_working_hours, delete_all_data, add_reservation, save_user_account
def create_mock_datas(app: Flask):
    #delete_all_data() # Uncomment this line to delete all data
    user_data = {
        "full_name": "Test User Restaurant Owner",
        "email": "testuser@example.com",
        "phone": "1234567890",
        "profile_image_url": "http://example.com/image.jpg",
        "user_type": "admin",
        "password_hash": "passwordhsh"
    }
    user = save_user_account(user_data)
    user_id = user.get('id')
    app.logger.info('user id', user_id)
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
    app.logger.info('restaurant id', restr_id)
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days_of_week:
        add_working_hours(restaurant_id=restr_id, day_of_week=day, opening_time="09:00", closing_time="21:00")
    table1 = add_table(table_number="1",restaurant_id=restr_id,number_of_seats=4, table_type="indoor", description="Table 1")
    table2 = add_table(table_number="2",restaurant_id=restr_id,number_of_seats=4, table_type="indoor", description="Table 2")
    table_id = table1.get('id')
    app.logger.info('table_id id: %s', table_id)
    reservation_start_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    reservation_end_time = reservation_start_time.replace(hour=10, minute=30)
    reservation_code = str(int(datetime.timestamp(datetime.now())))[-10:]
    add_reservation(user_id=user_id, restaurant_id=restr_id, dining_table_id=table_id, number_of_people=4, reservation_code=reservation_code,
                    reservation_start_time=reservation_start_time, reservation_end_time=reservation_end_time)

