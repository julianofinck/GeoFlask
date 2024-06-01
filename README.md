# Backend
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![ArcGIS Pro 3.2.2](https://img.shields.io/badge/argispro-v3.2.2-blue) 
![ArcPy v.3.2](https://img.shields.io/badge/arcpy-v3.2=py39_arcgispro_49743-blue)
![Python 3.9.18](https://img.shields.io/badge/python-v3.9.18-yellow) 
![WindowsOS](https://img.shields.io/badge/windowsOS--black)

This flask app reads layers in database, serve geojsons and allow updating to the database. The chosen database is a PostgreSQL+PostGIS.

To `Flask-Migrate` properly work with `geoalchemy2`, always define the geometry column with name **geom**

|Route|Function|
|---|---|
|ping| returns "pong"|
|upload|insert new geojson|
|query-geojson| returns geojson|

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


# ERRORS
I learned there is an error when using SQLAlchemy + geoalchemy2 together. They both create spatial index differently and end up creating it twice. A way to overcome it is to set geoalchemy2.Geometry columns with spatial_index=False set spatial indexes explicitly.

Other way is to ignore in the migrations/env.py objects that are "idx_%_geom" but this imply having all your geometry columns named the same.