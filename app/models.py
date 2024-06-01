from .extensions import db
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Index


class GeoData(db.Model):
    # In Flask CamelCase gets translated to snake_case
    __tablename__ = 'geo_data'

    id = db.Column(db.Integer, primary_key=True)
    properties = db.Column(JSONB)
    geom = db.Column(Geometry('POLYGON', spatial_index=False, srid=4674))  # Define geometry column with GeoAlchemy2

    __table_args__ = (
        Index('idx_geo_data_geom', geom, postgresql_using='gist'),
    )

