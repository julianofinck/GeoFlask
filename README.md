# Backend
This flask app reads layers in database, serve geojsons and allow updating to the database. The chosen database is a PostgreSQL+PostGIS.

|Route|Function|
|---|---|
|ping| returns "pong"|
|upload|insert new geojson|
|query-geojson| returns geojson|

query must return
```js
var geojsonFeature = {
    "type": "Feature",
    "properties": {
        "name": "Coors Field",
        "amenity": "Baseball Stadium",
        "popupContent": "This is where the Rockies play!"
    },
    "geometry": {
        "type": "Point",
        "coordinates": [-104.99404, 39.75621]
    }
};
```

## Tests
Run tests with `pytest tests/`


# Run flask
flask --app app run --debug

### Database
#### Database - install DB in WSL
```bash
sudo apt update
sudo apt install postgis

# Check status
sudo service postgresql status

# Enter
cp comando.sql /tmp/comando.sql
sudo -u postgres psql -f comando.sql
```
Create the database
```SQL
-- Create DATABASE with postgis and SUPERUSER
CREATE DATABASE myapp;
CREATE EXTENSION postgis;
CREATE ROLE myuser WITH LOGIN PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE myapp TO myuser;
```
#### Database - First migration
Start the database.
The "migration" folder must be empty.
Open the container terminal and type the following
```bash
# Remove any existing migrations file
rm -r migrations/*

# Initialize db
flask db init

# Alembic requires custom types to be
#  included in. Column from geoalchemy2
#  is such a type.
#
# Edit "migrations/script.py.mako" and 
#  add "import geoalchemy2". This way
#  alembic will always have it added to
#  migration scripts:

(...)
from alembic import op
import sqlalchemy as sa
import geoalchemy2
${imports if imports else ""}
(...)

# Choose your .env names wise.
# flask overwrites "DATABASE_HOSTNAME"
flask db migrate -m "Initial migration."
flask db upgrade
```
[About Alembic and custom types](https://stackoverflow.com/questions/39215278/alembic-migration-for-geoalchemy2-raises-nameerror-name-geoalchemy2-is-not-de)