from datetime import datetime
def parse_time_slot(reservation_date,time_slot ):
        start_hour, end_hour = time_slot.split('-')
        start_time_str = f"{reservation_date} {start_hour}"
        end_time_str = f"{reservation_date} {end_hour}"
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
        return start_time, end_time