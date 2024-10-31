from app.data.models import Reservation
from flask import Flask, render_template, request
from data.db_session import session
app = Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/reservation_form')
def reservation_form():
    return render_template('reservation_form.html')

@app.route('/reserve_table')
def reserve_table():
    data = request.get_json()
    if not data:
        return 'No data provided', 400

    user_id = data.get('user_id')
    restaurant_id = data.get('restaurant_id')
    dining_table_id = data.get('dining_table_id')
    number_of_people = data.get('number_of_people')
    reservation_start_time = data.get('reservation_start_time')
    reservation_end_time = data.get('reservation_end_time')
    status = data.get('status')
    special_requests = data.get('special_requests')
    reservation_code = data.get('reservation_code')

    if not all([user_id, restaurant_id, dining_table_id, number_of_people, reservation_start_time, reservation_end_time, status, reservation_code]):
        return 'Missing required fields', 400
    
    # Save reservation to database
    reservation = Reservation(
        user_id=user_id,
        restaurant_id=restaurant_id,
        dining_table_id=dining_table_id,
        number_of_people=number_of_people,
        reservation_start_time=reservation_start_time,
        reservation_end_time=reservation_end_time,
        status=status,
        special_requests=special_requests,
        reservation_code=reservation_code
    )
    
    try:
        session.add(reservation)
        session.commit()
    except Exception as e:
        session.rollback()
        return str(e), 500

    return 'Reservation saved', 201