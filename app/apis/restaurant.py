from services.db_service import get_all_restaurants, add_restaurant
from flask_restx import Namespace, Resource, fields

api=Namespace("restaurant", path="/api/v1/restaurant", description="Operations for getting the restaurant information")

@api.route("/")
class Restaurant(Resource):
    @api.doc("Add a new restaurant")
    @api.expect(api.model('Restaurant', {
        'name': fields.String(required=True, description='The restaurant name'),
        'description': fields.String(required=False, description='The restaurant description'),
        'location_address': fields.String(required=False, description='The restaurant address'),
        'location_latitude': fields.String(required=True, description='The restaurant latitude'),
        'location_longitude': fields.String(required=True, description='The restaurant longitude'),
        'restaurant_image': fields.String(required=False, description='The restaurant image'),
        'time_zone': fields.String(required=False, description='The restaurant time zone'),
        'owner_user_id': fields.String(required=False, description='The owner user ID')
    }))
    @api.response(201, description="Restaurant successfully created")
    @api.response(400, description="Invalid input")
    def post(self):
        try:
            restaurant_data = api.payload
            if not restaurant_data:
                return 'Invalid input', 400
            restaurant = add_restaurant(restaurant_data=restaurant_data)
            return restaurant.get('id'), 201
        except Exception as e:
            print(e)
            return 'Invalid request', 400

    @api.doc("Get restaurants") 
    @api.response(200,description="restaurants list")
    def get(self):
        try:
            result = get_all_restaurants()
            if not result:
                return 'No restaurant found', 404
            return result, 200
        except Exception as e:
            print(e)
            return 'Invalid request', 400
