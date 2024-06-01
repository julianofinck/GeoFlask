import shapely
from flask import Blueprint, jsonify
from ..models import GeoData # get the name of all models

geojson_bp = Blueprint('geojson', __name__)

@geojson_bp.route("/geojson", methods=['GET'])
def geojson():
    # Fetch geodata from the GeoData model
    geodata_objects = GeoData.query.all()

    # Convert geodata objects to GeoJSON format
    features = []

    for data in geodata_objects:
        feature = {
            "type": "Feature",
            # Adjust as per your model structure
            "properties": data.properties,  
            # Assuming you already have the geometry in GeoJSON format
            "geometry": shapely.geometry.mapping(shapely.from_wkb(str(data.geom)))
        }
        features.append(feature)

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    return jsonify(geojson_data)