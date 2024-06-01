import os
import shutil
import tempfile
import zipfile

import geopandas as gpd
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import GeoData

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
@cross_origin()
def upload_file():
    # Validate request
    result = validate(request)
    if isinstance(result, tuple):
        return result
    else:
        gdf = result

    # Save GeoJSON data to PostgreSQL
    for _, row in gdf.iterrows():
        geom_wkt = row.geometry.wkt  # geoalchemy2 reads from wkt
        properties = row.drop("geometry").to_dict()
        geodata = GeoData(properties=properties, geom=geom_wkt)
        db.session.add(geodata)

    db.session.commit()

    return (
        jsonify(
            {"message": "Success! File uploaded, processed and inserted in database"}
        ),
        200,
    )


def validate(request):
    # Shapefile part in data of request
    if "shapefile" not in request.files:
        return jsonify({"error": "No shapefile part in data of POST request"}), 400

    file = request.files["shapefile"]

    # Must have files
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Must be .zip
    if not file.filename.endswith(".zip"):
        return (
            jsonify({"error": "Invalid file format. Only zip files are allowed."}),
            400,
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        # save .zip
        filename = secure_filename(file.filename)
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)
        # unzip
        with zipfile.ZipFile(filepath, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Validate if .shp is inside it
        shp_path = None
        for extracted_file in zip_ref.namelist():
            if extracted_file.endswith(".shp"):
                shp_path = os.path.join(temp_dir, extracted_file)
                break

        if shp_path is None:
            shutil.rmtree(temp_dir)
            return jsonify({"error": "No .shp file found in the zip"}), 400

        # Read .shp file to GeoDataFrame
        gdf = gpd.read_file(shp_path)

    # Check if it is POLYGON
    if not all([geom_type == "Polygon" for geom_type in gdf.geometry.type]):
        return jsonify({"error": "Shapefile must be polygon."}), 400

    # Validate Spatial Reference - SIRGAS 2000 (EPSG: 4674)
    if gdf.crs.to_epsg() != 4674:
        return (
            jsonify(
                {
                    "error": "Invalid spatial reference. The .shp file must have SRID 4674."
                }
            ),
            400,
        )

    return gdf
