# GeoFlask - Backend API
[![Python 3.10.12](https://img.shields.io/badge/Python-v3.10.12-yellow)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-v1.1.2-brightgreen)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-v14.12-blue)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-v3.1-blue)](https://postgis.net/)


## Description

A Flask app that uses PostgreSQL with PostGIS for geospatial data, providing endpoints for querying and uploading polygon GeoJSON data.

|Route|Function|
|---|---|
|`GET /ping`| returns "pong"|
|`POST /upload`|insert new geojson|
|`GET /geojson`| returns geojson|


## Dependencies

Python 3.10.12 and `requirements.txt`


## Getting Started

Lores ipsum

### Flask-Migrate

To `Flask-Migrate`'s **Alembic** properly work with **geoalchemy2** and **sqlachemy**, declare any geometry column with `spatial_index=False` and add the spatial_index explicitly.

Or make sure to ignore in the `migrations/env.py` objects that are "idx_%_geom" but this imply having all your geometry columns named the same.




## Tests
Run tests with `pytest --cov=app tests/ -v`


# Run flask
flask --app app run --debug

### Database
#### Database - install DB in WSL
```bash
# Start from scratch without any conflict
sudo apt-get --purge remove postgresql postgresql-common postgresql-client postgresql-contrib postgis
sudo apt-get autoremove

# Install
sudo apt update
sudo apt-get install postgresql postgresql-contrib postgis 

# Check status
sudo service postgresql status

# Enter
sudo -u postgres psql -f comando.sql
```
Create the database
```SQL
-- Create DATABASE with postgis and SUPERUSER
CREATE DATABASE <FLASK_DB_NAME>;
CREATE ROLE <FLASK_DB_USERNAME> WITH LOGIN PASSWORD <FLASK_DB_PASSWORD> SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE <FLASK_DB_NAME> TO <FLASK_DB_USERNAME>;

\c <FLASK_DB_NAME>
CREATE EXTENSION postgis;
```
## Flask-Migrate
On the first migration, run
```bash
# Init fladk db from scratch
rm -r migrations/*
flask db init
```
Edit `migrations/script.py.mako` by adding `import geoalchemy2` to tell Alembic you have geoalchemy2 geometry columns
```py
# ...
from alembic import op
import sqlalchemy as sa
import geoalchemy2
${imports if imports else ""}
# ...
```
Edit `migrations/env.py` to ignore postgis tables
```py
def get_metadata():
# ...

def include_object(object, name, type_, reflected, compare_to):    
    if type_ == "table" and name == 'spatial_ref_sys':
        return False
    else:
        return True


def run_migrations_offline():
    # ...
    context.configure(
        # ...
        include_object=include_object       # <--- HERE
        )
    # ...

def run_migrations_online():
    # ...
    with connectable.connect() as connection:
        context.configure(
            # ...
            include_object=include_object
        )
```

```bash
# Choose your .env names wise.
# flask overwrites "DATABASE_HOSTNAME"
flask db migrate -m "Initial migration."
flask db upgrade
```
[About Alembic and custom types](https://stackoverflow.com/questions/39215278/alembic-migration-for-geoalchemy2-raises-nameerror-name-geoalchemy2-is-not-de)
