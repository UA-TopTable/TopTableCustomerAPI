from flask import request
from services.db_service import get_all_tables, get_table_available_time_slots
from flask_restx import Namespace, Resource

api=Namespace("table", path="/api/v1/table",description="Operations for getting the table information")

@api.route("/")
class RestaurantTableAvailability(Resource):
    @api.doc("Get tables and their available time slots")
    @api.param("restaurant_id", "The ID of the restaurant", required=True)
    @api.param("reservation_date", "The date of the reservation", required=True)
    @api.response(200, description="tables and their available time slots")
    @api.response(404, "No table found")
    def get(self):
        restaurant_id = request.args.get('restaurant_id')
        reservation_date = request.args.get('reservation_date')
        
        if not restaurant_id or not reservation_date:
            return 'Missing parameters', 400
        
        try:
            tables = get_all_tables(restaurant_id)
            if not tables:
                return 'No table found', 404
            for table in tables:
                table_id = table.get('id')
                avaliable_slots = get_table_available_time_slots(restaurant_id, table_id, reservation_date)
                if not avaliable_slots:
                    table.update({'available_time_slots': []})
                else:
                    table.update({'available_time_slots': avaliable_slots})
            return tables, 200
        except Exception as e:
            print(e)
            return 'Invalid request', 400