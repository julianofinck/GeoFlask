# curl -X POST -F 'file=@path_to_your_zip_file.zip' http://127.0.0.1:5000/api/upload
from flask import Blueprint, request, jsonify
import zipfile
import os
import geopandas as gpd
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import GeoData


upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'shapefile' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['shapefile']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not file.filename.endswith('.zip'):
        return jsonify({'error': 'Invalid file format. Only zip files are allowed.'}), 400
    
    # Extract .zip temporarily save to disk
    filename = secure_filename(file.filename)
    filepath = os.path.join('/tmp', filename)
    file.save(filepath)
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall('/tmp')
    
    # Validate if .shp is inside it
    shp_path = None
    for extracted_file in zip_ref.namelist():
        if extracted_file.endswith('.shp'):
            shp_path = os.path.join('/tmp', extracted_file)
            break
    
    if shp_path is None:
        # TODO: REMOVE what was extracted if not valid.
        return jsonify({"error": "No .shp file found in the zip"}), 400
    
    # Read .shp file and convert to GeoJSON
    gdf = gpd.read_file(shp_path)

    # Validate Spatial Reference - SIRGAS 2000 (EPSG: 4674)
    if gdf.crs.to_epsg() != 4674:
        return jsonify({'error': 'Invalid spatial reference. The .shp file must have SRID 4674.'}), 400
    
    geojson_data = gdf.to_json()

    print('1'*100)
    
    # Save GeoJSON data to PostgreSQL
    for _, row in gdf.iterrows():
        geom = row.geometry.wkb
        properties = row.drop('geometry').to_dict()
        geodata = GeoData(properties=properties, wkb=geom)
        db.session.add(geodata)
    
    db.session.commit()
    
    return jsonify({"success": "File uploaded and processed successfully"}), 200
