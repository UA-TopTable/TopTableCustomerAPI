from data.models.DiningTable import DiningTable
from data.models.Reservation import Reservation
from sqlalchemy.orm import Session
from data.db_engine import engine

def add_reservation(user_id,restaurant_id,dining_table_id,number_of_people,reservation_start_time,reservation_end_time,
            status,special_requests,reservation_code):
    with Session(engine) as session:
        table = session.get(DiningTable, dining_table_id)
        if table is None:
            return "Table does not exist"
        
        reservation = Reservation(
            user_id=user_id,
            restaurant_id=restaurant_id,
            dining_table_id=dining_table_id,
            number_of_people=number_of_people,
            reservation_start_time=reservation_start_time,
            reservation_end_time=reservation_end_time,
            status=status,
            special_requests=special_requests,
            reservation_code=reservation_code)
        session.add(reservation)
        session.commit()
        return reservation.as_dict() if reservation else None

def get_reservation(reservation_id):
    with Session(engine) as session:
        reservation = session.get(Reservation, reservation_id)
        return reservation.as_dict() if reservation else None