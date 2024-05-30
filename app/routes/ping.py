from flask import Blueprint
from ..extensions import db
from ..models import GeoData


ping_bp = Blueprint('ping', __name__)

@ping_bp.route("/ping", methods=['GET'])
def hello():
    return "Pong!"
