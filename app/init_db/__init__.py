"""
Create the database with postgis extension
Create the user with full privileges


It must try to connect with the .env file infos.
If it fails, it must try to look for a "PG_PASSWORD".
If it has no "PG_PASSWORD", it print the absence of the variable and tries to run with "sudo -u postgres psql"
"""

import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

from . import as_dba
from . import as_flask_user


def bootstart():
    recreate_db = os.getenv("RECREATE_DB", "1")
    if int(recreate_db) == 1:
        create_db()


def create_db():
    # Load superuser username and password
    pg_username = os.getenv("PG_USER")
    if pg_username is None or pg_username == '':
        raise NameError("PG_USER not found")
    pg_password = os.getenv("PG_PASS")

    # Set PG_PASSWORD if not set
    if pg_password is None or pg_password == '':
        pg_password = set_pg_password(pg_username)

    # Load database hostname and port
    hostname = os.getenv("DB_HOSTNAME")
    port = os.getenv("DB_PORT")

    # Load the flask database name
    flask_db_name = os.getenv('DB_NAME')
    flask_db_username = os.getenv('DB_USERNAME')
    flask_db_password = os.getenv('DB_PASSWORD')

    # Recreate the database and flask user
    pg_params = {
        "host": hostname,
        "port": port,
        "dbname": "postgres",
        "user": pg_username,
        "password": pg_password
    }
    as_dba.recreate_database(
        pg_params, 
        flask_db_name, 
        flask_db_username, 
        flask_db_password)

    # Enable postgis in the flask database
    flask_db_params = {
        "host": hostname,
        "port": port,
        "dbname": flask_db_name,
        "user": flask_db_username,
        "password": flask_db_password
    }
    as_flask_user.enable_postgis(flask_db_params)

    # Disable recreation of the database
    adjust_dotenv("RECREATE_DB", "0")

def adjust_dotenv(
        env:str, 
        value:str
        ):
    # Read
    lines = []
    with open(".env", "r") as f:
        for l in f:
            lines.append(l)

    # Check if env exists 
    has_env = False
    for i, line in enumerate(lines):
        if env in line:
            lines[i] = f"{env}={value}\n"
            has_env = True
            break

    # Add env if not exists
    if not has_env:
        lines.append(f"{env}={value}\n")

    # Write
    with open(".env", "w") as f:
        for l in lines:
            f.write(l)


def set_pg_password(pg_username):
    print("No PG_PASS found. Setting it to 'postgres'. Trying with 'sudo -u postgres psql'")
    pg_password = "postgres"
    alter_password = f"ALTER ROLE {pg_username} WITH PASSWORD '{pg_password}';"
    try:
        subprocess.run(["sudo", "-u", "postgres", "psql", "-c", alter_password], check=True)
        adjust_dotenv("DB_PG_PASS", pg_password)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
