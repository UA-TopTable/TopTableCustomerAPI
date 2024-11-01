from services.db_service import get_all_restaurants
from flask_restx import Namespace, Resource

api=Namespace("restaurant",description="Operations for getting the restaurant information")

@api.route("/")
class Restaurant(Resource):
    @api.doc("Get restaurants") 
    @api.response(200,description="restaurants list")
    def get(self):
        try:
            result = get_all_restaurants()
            if not result:
                return 'Reservation not found', 404
            return result, 200
        except Exception as e:
            print(e)
            return 'Invalid request', 400
