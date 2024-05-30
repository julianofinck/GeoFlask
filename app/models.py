from .extensions import db
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB


class GeoData(db.Model):
    # In Flask CamelCase gets translated to snake_case
    __tablename__ = 'geo_data'
    id = db.Column(db.Integer, primary_key=True)
    properties = db.Column(JSONB)
    geometry = db.Column(Geometry('POLYGON'))  # Define geometry column with GeoAlchemy2
