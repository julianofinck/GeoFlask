# pip install pytest-cov
import os
import zipfile
import io
from flask import url_for
from app import create_app, db
from app.models import GeoData
from app.config import TestConfig
import pytest


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

def test_upload(client):
    data = {
        'file': (create_test_zip(), 'test.zip')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert response.json['message'] == 'File successfully processed and data inserted into the database.'

    with client.application.app_context():
        geo_data_count = GeoData.query.count()
        assert geo_data_count == 1
