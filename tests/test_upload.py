# curl -X POST -F 'file=@tests/shp.zip' http://127.0.0.1:5000/api/upload

# pip install pytest-cov
import io
import os
import tempfile
import zipfile

import geopandas as gpd
import pytest
import shapely
from flask import url_for
from shapely.geometry import Point, Polygon

from app import create_app, db
from app.config import TestConfig
from app.models import GeoData


class TestValidate:
    def test_no_file_part(self, client):
        response = client.post("/upload")
        assert response.status_code == 400
        assert response.json["error"] == "No shapefile part in data of POST request"

    def test_no_selected_file(self, client):
        data = {"shapefile": (io.BytesIO(b""), "")}
        response = client.post("/upload", data=data)
        assert response.status_code == 400
        assert response.json["error"] == "No selected file"

    def test_not_a_zip_file(self, client):
        data = {"shapefile": (io.BytesIO(b"not a zip"), "not_a_zip.file")}
        response = client.post("/upload", data=data)
        assert response.status_code == 400
        assert (
            response.json["error"] == "Invalid file format. Only zip files are allowed."
        )

    def test_no_shp_in_zip(self, client):
        data = {"shapefile": (create_test_zip(["shx"]), "mock.zip")}
        response = client.post("/upload", data=data)
        assert response.status_code == 400
        assert response.json["error"] == "No .shp file found in the zip"
        # Make sure no shp file was created

    def test_not_polygon_in_shp(self, client):
        data = {"shapefile": (create_test_zip(geom="point"), "mock.zip")}
        response = client.post("/upload", data=data)
        assert response.status_code == 400
        assert response.json["error"] == "Shapefile must be polygon."
        # Make sure no shp file was created

    def test_shp_with_wrong_crs(self, client):
        data = {"shapefile": (create_test_zip(crs="EPSG:4326"), "mock.zip")}
        response = client.post("/upload", data=data)
        assert response.status_code == 400
        assert (
            response.json["error"]
            == "Invalid spatial reference. The .shp file must have SRID 4674."
        )
        # Make sure no shp file was created


def create_test_zip(exts=["shp", "shx", "dbf", "prj"], crs="EPSG:4674", geom="polygon"):
    # Create a mock shapefile with a rectangle polygon
    if geom == "polygon":
        polygon = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    elif geom == "point":
        polygon = Point((0, 30))
    else:
        raise NotImplementedError(f"Invalid geometry type: {geom}")
    gdf = gpd.GeoDataFrame([{"geometry": polygon}], crs=crs)

    # Save the GeoDataFrame to a temporary directory
    with tempfile.TemporaryDirectory() as tempdir:
        shp_path = f"{tempdir}/test.shp"
        gdf.to_file(shp_path)

        # Zip the shapefile components
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for ext in exts:
                filename = f"test.{ext}"
                filepath = f"{tempdir}/{filename}"
                with open(filepath, "rb") as f:
                    zf.writestr(filename, f.read())

    zip_buffer.seek(0)
    return zip_buffer


def test_correct_upload(client):
    data = {"shapefile": (create_test_zip(), "mock.zip")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert (
        response.json["message"]
        == "Success! File uploaded, processed and inserted in database"
    )

    with client.application.app_context():
        geo_data_count = GeoData.query.count()
        assert geo_data_count == 1
