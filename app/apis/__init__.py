from flask import Blueprint
from flask_restx import Api, Namespace
from flask_restx.apidoc import apidoc

from .auth import api as api_auth
from .reservation import api as api_reservation
from .restaurant import api as api_restaurant
from .dining_table import api as api_table
from .ui import api as api_ui
from secret import ROOT_PATH_PREFIX

from secret import ROOT_PATH_PREFIX

blueprint = Blueprint('apis', __name__, url_prefix=ROOT_PATH_PREFIX)

apidoc.static_url_path = f'{ROOT_PATH_PREFIX}/swaggerui'

api = Api(version="1.0",
        title="TopTable Customer API",
        description="TopTable API for the customer side",
        prefix=ROOT_PATH_PREFIX,
        doc=f'{ROOT_PATH_PREFIX}' )

api.add_namespace(api_auth)
api.add_namespace(api_reservation)
api.add_namespace(api_restaurant)
api.add_namespace(api_ui)
api.add_namespace(api_table)