"""
This script must run the following commands in the PostgreSQL server.

It must try to connect with the .env file infos.
If it fails, it must try to look for a "PG_PASSWORD".
If it has no "PG_PASSWORD", it print the absence of the variable and tries to run with "sudo -u postgres psql"
"""
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

recreate_db = int(os.getenv("RECREATE_DB", "1"))


CREATE_DB = """-- Create DATABASE with postgis and SUPERUSER
CREATE DATABASE myapp;
CREATE EXTENSION postgis;
CREATE ROLE myuser WITH LOGIN PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE myapp TO myuser;"""

if recreate_db == 1:
    with open(".env", "a") as f:
        f.write("\n")
        f.write("# DANGER - Change to True to recreate\n")
        f.write("RECREATE_DB=0\n")
        f.write("\n")

    # Create DB
    params = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USERNAME"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOSTNAME"),
        "port": os.getenv("DB_PORT")}
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_DB)
            output = cur.fetchall()
            print("Created DB!")
