from flask import Blueprint
from flask_restx import Api

blueprint = Blueprint('apis', __name__)

api = Api(version="1.0",title="TopTable Customer API",description="TopTable API for the customer side",prefix="/api/v1")

from .auth import api as api_auth
from .reservation import api as api_reservation
api.add_namespace(api_auth)
api.add_namespace(api_reservation)