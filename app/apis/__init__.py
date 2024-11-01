from flask import Blueprint
from flask_restx import Api, Namespace

from .auth import api as api_auth
from .reservation import api as api_reservation
from .restaurant import api as api_restaurant
from .ui import api as api_ui

blueprint = Blueprint('endpoints', __name__)

api = Api(version="1.0", title="TopTable Customer API", description="TopTable API for the customer side", prefix="/api/v1")

api.add_namespace(api_auth)
api.add_namespace(api_reservation)
api.add_namespace(api_restaurant)
api.add_namespace(api_ui)