# curl -X POST -F 'file=@path_to_your_zip_file.zip' http://127.0.0.1:5000/api/upload
from flask import Blueprint, request, jsonify
import zipfile
import os
import geopandas as gpd
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import GeoData
from ..utils import generate_random_string
import shutil
import tempfile


upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'shapefile' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['shapefile']
    
    # Must have files
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Must be .zip
    if not file.filename.endswith('.zip'):
        return jsonify({'error': 'Invalid file format. Only zip files are allowed.'}), 400
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # save .zip
        filename = secure_filename(file.filename)
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)

        # unzip
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    
        # Validate if .shp is inside it
        shp_path = None
        for extracted_file in zip_ref.namelist():
            if extracted_file.endswith('.shp'):
                shp_path = os.path.join(temp_dir, extracted_file)
                break
    
        if shp_path is None:
            shutil.rmtree(temp_dir)
            return jsonify({"error": "No .shp file found in the zip"}), 400
    
        # Read .shp file and convert to GeoJSON
        gdf = gpd.read_file(shp_path)

    # Check if it is POLYGON
    if not all([geom_type == 'Polygon' for geom_type in gdf.geometry.type]):
        return jsonify({'error': 'Shapefile must be polygon.'}), 400

    # Validate Spatial Reference - SIRGAS 2000 (EPSG: 4674)
    if gdf.crs.to_epsg() != 4674:
        return jsonify({'error': 'Invalid spatial reference. The .shp file must have SRID 4674.'}), 400
    
    # Get it as GeoJSON
    geojson_data = gdf.to_json()

    # Save GeoJSON data to PostgreSQL
    for _, row in gdf.iterrows():
        geom_wkb = row.geometry.wkb
        properties = row.drop('geometry').to_dict()
        geodata = GeoData(properties=properties, geometry=geom_wkb)
        db.session.add(geodata)
    
    db.session.commit()
    
    return jsonify({"success": "File uploaded and processed successfully"}), 200
