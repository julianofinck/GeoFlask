# curl -X POST -F 'file=@tests/shp.zip' http://127.0.0.1:5000/api/upload

# pip install pytest-cov
import os
import zipfile
import io
from flask import url_for
from app import create_app, db
from app.models import GeoData
from app.config import TestConfig
import pytest


def test_validation_no_file(client):
    response = client.post('/upload')
    assert response.status_code == 400
    assert response.json["error"] == "No file part"

def test_no_selected_file(client):
    data = {
        'shapefile': (io.BytesIO(b''), '')
    }
    response = client.post('/upload', data=data)
    assert response.status_code == 400
    assert response.json["error"] == "No selected file"

def test_no_file3(client):
    response = client.post('/upload')
    assert response.status_code == 400
    assert response.json["error"] == "No file part"


def create_test_zip():
    # Create a mock shapefile and zip it
    shp_content = (
        "dummy shapefile content"  # Replace with actual content of a dummy .shp file if needed
    )
    prj_content = "dummy prj content"
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('test.shp', shp_content)
        zf.writestr('test.prj', prj_content)
    
    zip_buffer.seek(0)
    return zip_buffer

def teast_upload(client):
    data = {
        'file': (create_test_zip(), 'test.zip')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert response.json['message'] == 'File successfully processed and data inserted into the database.'

    with client.application.app_context():
        geo_data_count = GeoData.query.count()
        assert geo_data_count == 1
