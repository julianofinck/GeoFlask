import psycopg2
from psycopg2 import sql

def recreate_database(params, flask_db_name, flask_db_username, flask_db_password):
    # Dont use "with", it gets into transaction mode and disables CREATE and DROP
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()

    terminate_active_connections(cur, flask_db_name)
    drop_database(cur, flask_db_name)
    create_database(cur, flask_db_name)
    create_superuser(cur, flask_db_username, flask_db_password, flask_db_name)

    cur.close()
    conn.close()

def terminate_active_connections(cur, dbname):
    cur.execute(sql.SQL("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s"), [dbname])
    print(f"Terminated active connection to {dbname}")

def drop_database(cur, dbname):
    cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(dbname)))
    print(cur.statusmessage, dbname)

def create_database(cur, dbname):
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
    print(cur.statusmessage, dbname)    

def create_superuser(cur, flask_db_user, flask_db_password, flask_db_name):
    cur.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(flask_db_user)))
    print(cur.statusmessage, flask_db_user)

    cur.execute(sql.SQL("CREATE USER {} WITH ENCRYPTED PASSWORD {} SUPERUSER").format(sql.Identifier(flask_db_user), sql.Literal(flask_db_password)))
    print(cur.statusmessage, flask_db_user)

    cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(sql.Identifier(flask_db_name), sql.Identifier(flask_db_user)))
    print(cur.statusmessage, flask_db_user, "ON", flask_db_name)
