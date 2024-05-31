import psycopg2


def enable_postgis(params: dict[str: str]) -> None:
    # Enable postgis
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            result = cur.statusmessage
            print(result, "PostGIS")
