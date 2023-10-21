#! /usr/bin/env python3

import psycopg2
from pgcopy import CopyManager

CONNECTION = "postgres://postgres:password@localhost:5432/levylab"
# CONNECTION = "postgres://postgres:password@10.0.0.56:5432/levylab"


def get_some_data(conn:psycopg2.extensions.connection):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensor_data LIMIT 5;")
    for row in cursor.fetchall():
        print(row)

    query = "SELECT COUNT(*) FROM sensor_data;"
    cursor.execute(query)
    print(cursor.fetchall())

    query = """
           SELECT time_bucket('5 minutes', time) AS five_min, avg(cpu)
           FROM sensor_data
           JOIN sensors ON sensors.id = sensor_data.sensor_id
           WHERE sensors.location = %s AND sensors.type = %s
           GROUP BY five_min
           ORDER BY five_min DESC;
           """
    location = "floor"
    sensor_type = "a"
    data = (location, sensor_type)
    cursor.execute(query, data)
    results = cursor.fetchall()

    print(len(results))
    cursor.close()


with psycopg2.connect(CONNECTION) as conn:
    # create_tables(conn)
    # fast_insert(conn)
    get_some_data(conn)
