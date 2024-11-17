from decimal import Decimal
from data.models.WorkingHours import WorkingHours
from data.models.DiningTable import DiningTable
from data.models.Reservation import Reservation
from data.models.Restaurant import Restaurant
from data.models.UserAccount import UserAccount
from data.models.RestaurantPictures import RestaurantPictures
from sqlalchemy.orm import Session
from data.db_engine import engine
    
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

def add_reservation(user_id,restaurant_id,dining_table_id,number_of_people,reservation_start_time
                    ,reservation_end_time,reservation_code,special_requests=''):
    with Session(engine) as session:
        table = session.get(DiningTable, dining_table_id)
        if table is None:
            return None
        
        reservation = Reservation(
            user_id=user_id,
            restaurant_id=restaurant_id,
            dining_table_id=dining_table_id,
            number_of_people=number_of_people,
            reservation_start_time=reservation_start_time,
            reservation_end_time=reservation_end_time,
            status='pending',
            special_requests=special_requests,
            reservation_code=reservation_code)
        session.add(reservation)
        session.commit()
        return reservation.as_dict() if reservation else None

def get_reservation(reservation_id):
    with Session(engine) as session:
        reservation = session.get(Reservation, reservation_id)
        return reservation.as_dict() if reservation else None


def get_table_available_time_slots(restaurant_id, table_id, reservation_date):
    with Session(engine) as session:
        # Get the working hours for the given day of the week
        reservation_date = datetime.strptime(reservation_date, '%Y-%m-%d').date()
        day_of_week = reservation_date.strftime('%A').lower()
        working_hours = session.query(WorkingHours).filter(
            WorkingHours.restaurant_id == restaurant_id,
            WorkingHours.day_of_week == day_of_week
        ).first()

        if not working_hours:
            return []  # Restaurant is closed on this day

        # Define the restaurant's operating hours
        opening_time = datetime.combine(reservation_date, working_hours.opening_time)
        closing_time = datetime.combine(reservation_date, working_hours.closing_time)

        # Get all reservations for the given table on the specified date
        reservations = session.query(Reservation).filter(
            Reservation.restaurant_id == restaurant_id,
            Reservation.dining_table_id == table_id,
            and_(
                Reservation.reservation_start_time >= opening_time,
                Reservation.reservation_start_time < closing_time
            )
        ).order_by(Reservation.reservation_start_time).all()

        # Generate all possible half-hour slots
        all_slots = []
        current_slot_start = opening_time
        while current_slot_start < closing_time:
            slot_end = current_slot_start + timedelta(minutes=30)
            if slot_end <= closing_time:
                all_slots.append((current_slot_start, slot_end))
            current_slot_start = slot_end
        # Remove occupied slots
        available_slots = all_slots.copy()
        for reservation in reservations:
            available_slots = [
                slot for slot in available_slots
                if not (reservation.reservation_start_time < slot[1] and
                        reservation.reservation_end_time > slot[0])
            ]

        # Format the available slots
        formatted_slots = [
            f"{slot[0].strftime('%H:%M')}-{slot[1].strftime('%H:%M')}"
            for slot in available_slots if isinstance(slot[0], datetime) and isinstance(slot[1], datetime)
        ]

        return formatted_slots
    
def add_restaurant(restaurant_data: dict):
    with Session(engine) as session:
        restaurant = Restaurant(
            name=restaurant_data['name'],
            description=restaurant_data.get('description'),
            location_address=restaurant_data.get('location_address'),
            location_latitude=Decimal(str(restaurant_data['location_latitude'])),
            location_longitude=Decimal(str(restaurant_data['location_longitude'])),
            restaurant_image=restaurant_data.get('restaurant_image'),
            time_zone=restaurant_data.get('time_zone'),
            owner_user_id=restaurant_data.get('owner_user_id')
        )
        session.add(restaurant)
        session.commit()
        return restaurant.as_dict() if restaurant else None
    
def get_restaurant(restaurant_id):
    with Session(engine) as session:
        restaurant=session.get(Restaurant,restaurant_id)
        return restaurant.as_dict() if restaurant else None
    
def get_all_restaurants():
    with Session(engine) as session:
        restaurants=session.query(Restaurant).order_by(Restaurant.id).all()
        return [restaurant.as_dict() for restaurant in restaurants] if restaurants else None
    
def get_all_tables(restaurant_id):
    with Session(engine) as session:
        tables=session.query(DiningTable).filter(DiningTable.restaurant_id==restaurant_id).all()
        return [table.as_dict() for table in tables] if tables else None

def add_table(table_number,number_of_seats,table_type,restaurant_id,description=''):
    if get_restaurant(restaurant_id) is None:
        return "restaurant does not exist"
    if table_type not in ["indoor","outdoor"]:
        return "table_type must be either 'indoor' or 'outdoor'"
    if len(table_number)>3:
        return "table_number must not have more than 3 digits"
    table=DiningTable(table_number=table_number,number_of_seats=number_of_seats,table_type=table_type,restaurant_id=restaurant_id, description=description)
    
    with Session(engine) as session:
        session.add(table)
        session.commit()
        return table.as_dict() if table else None

def add_working_hours(restaurant_id,day_of_week,opening_time,closing_time):
    if get_restaurant(restaurant_id) is None:
        return "restaurant does not exist",404
    if day_of_week.lower() not in ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']:
        return "day_of_week must be a valid day of the week",400
    try:
        opening_time=datetime.strptime(opening_time,"%H:%M").time()
        closing_time=datetime.strptime(closing_time,"%H:%M").time()
    except ValueError:
        return "opening_time and closing_time must be in HH:MM format",400
    if opening_time>=closing_time:
        return "closing_time must be after opening_time",400
    with Session(engine) as session:
        working_hours=WorkingHours(restaurant_id=restaurant_id,day_of_week=day_of_week,opening_time=opening_time,closing_time=closing_time)
        session.add(working_hours)
        session.commit()
        return working_hours.as_dict() if working_hours else None

def delete_all_data():
    """
    Delete all data from the database
    """
    with Session(engine) as session:
        session.query(Reservation).delete()
        session.query(DiningTable).delete()
        session.query(WorkingHours).delete()
        session.query(Restaurant).delete()
        session.query(UserAccount).delete()
        session.commit()

def save_user_account(user_data: dict):
    if user_data.get('phone') is None:
        user_data['phone'] = ''
    if user_data.get('profile_image_url') is None:
        user_data['profile_image_url'] = ''
    if user_data.get('user_type') is None:
        user_data['user_type'] = 'customer'
    with Session(engine) as session:
        existing_user = session.query(UserAccount).filter(UserAccount.email == user_data.get('email')).first()
        if existing_user:
            existing_user.full_name = user_data.get('full_name')
            existing_user.phone = user_data.get('phone')
            existing_user.profile_image_url = user_data.get('profile_image_url')
            existing_user.user_type = user_data.get('user_type')
            existing_user.password_hash = user_data.get('password_hash')
            user = existing_user
        else:
            user = UserAccount(
            full_name=user_data.get('full_name'),
            email=user_data.get('email'),
            phone=user_data.get('phone'),
            profile_image_url=user_data.get('profile_image_url'),
            user_type=user_data.get('user_type'),
            password_hash=user_data.get('password_hash')
            )
        session.add(user)
        session.commit()
        
        return user.as_dict() if user else None

def get_user_account(user_id):
    with Session(engine) as session:
        user = session.get(UserAccount, user_id)
        return user.as_dict() if user else None
    
def get_user_by_email(email):
    try:
        with Session(engine) as session:
            return session.query(UserAccount).filter(UserAccount.email==email).one()
    except NoResultFound:
        return None
    
def add_picture(picture_link, restaurant_id):
    with Session(engine) as session :
        picture = RestaurantPictures(
            link = picture_link,
            restaurant_id = restaurant_id
        )
        session.add(picture)
        session.commit()
        return picture.as_dict() if picture else None
    
def get_pictures(restaurant_id):
    with Session(engine) as session :
        pictures = session.query(RestaurantPictures).filter(RestaurantPictures.restaurant_id == restaurant_id).all()
        return [picture.as_dict() for picture in pictures] if pictures else None


def modify_description(description, restaurant_id):
    if description == '' or description is None :
        description = ''
    with Session(engine) as session :
        restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not restaurant :
            return None
        restaurant.description = description
        session.commit()
        return restaurant.as_dict() if restaurant else None
    
def get_user_reservations(user_id,starts_after=None,ends_before=None,restaurant_id=None):
    with Session(engine) as session:
        query=session.query(Reservation).filter(Reservation.user_id==user_id)
        if starts_after is not None:
            query=query.filter(Reservation.reservation_start_time>=starts_after)
        if ends_before is not None:
            query=query.filter(Reservation.reservation_end_time<=ends_before)
        if restaurant_id is not None:
            query=query.filter(Reservation.restaurant_id==restaurant_id)
        return query.all()

def get_table_by_id(table_id):
    try:
        with Session(engine) as session:
            return session.query(DiningTable).filter(DiningTable.id==table_id).one()
    except NoResultFound:
        return None
    
def get_user_by_id(user_id):
    try:
        with Session(engine) as session:
            return session.query(UserAccount).filter(UserAccount.id==user_id).one()
    except NoResultFound:
        return None

def get_restaurant_by_id(restaurant_id):
    try:
        with Session(engine) as session:
            return session.query(Restaurant).filter(Restaurant.id==restaurant_id).one()
    except NoResultFound:
        return None
    
def delete_reservation(reservation_id):
    with Session(engine) as session:
        reservation = session.query(Reservation).filter(Reservation.id==reservation_id).first()
        if not reservation:
            return
        session.delete(reservation)
        session.commit()