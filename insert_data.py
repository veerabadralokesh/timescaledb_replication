#! /usr/bin/env python3

import psycopg2
from pgcopy import CopyManager

CONNECTION = "postgres://postgres:password@localhost:5432/levylab"


# CONNECTION = "dbname=levylab user=postgres password=password host=localhost port=5432 sslmode=require"


# insert using pgcopy
def fast_insert(conn: psycopg2.extensions.connection):
    cursor = conn.cursor()

    # for sensors with ids 1-4
    for id in range(1, 4, 1):
        data = (id,)
        # create random data
        simulate_query = """SELECT generate_series(now() - interval '24 hour', now(), interval '5 minute') AS time,
                                %s as sensor_id,
                                random()*100 AS temperature,
                                random() AS cpu;
                                """
        cursor.execute(simulate_query, data)
        values = cursor.fetchall()

        # column names of the table you're inserting into
        cols = ['time', 'sensor_id', 'temperature', 'cpu']

        # create copy manager with the target table and insert
        mgr = CopyManager(conn, 'sensor_data', cols)
        mgr.copy(values)

    # commit after all sensor data is inserted
    # could also commit after each sensor insert is done
    conn.commit()
    cursor.close()

def create_tables(conn: psycopg2.extensions.connection):
    cursor = conn.cursor()
    # use the cursor to interact with your database
    # cursor.execute("SELECT * FROM table")
    # cursor.execute("SELECT 'hello world'")
    cursor.execute("SELECT * FROM public.llab_063")
    print(cursor.fetchone())

    query_delete = "DROP TABLE IF EXISTS sensor_data;"
    cursor.execute(query_delete)
    conn.commit()

    query_delete = "DROP TABLE IF EXISTS sensors;"
    cursor.execute(query_delete)
    conn.commit()

    query_create_sensors_table = """CREATE TABLE IF NOT EXISTS sensors (
                                    id SERIAL PRIMARY KEY,
                                    type VARCHAR(50),
                                    location VARCHAR(50)
                                );
                                """
    cursor.execute(query_create_sensors_table)
    conn.commit()

    # create sensor data hypertable
    query_create_sensordata_table = """CREATE TABLE IF NOT EXISTS sensor_data (
                                        time TIMESTAMPTZ NOT NULL,
                                        sensor_id INTEGER,
                                        temperature DOUBLE PRECISION,
                                        cpu DOUBLE PRECISION,
                                        FOREIGN KEY (sensor_id) REFERENCES sensors (id)
                                    );
                                    """
    # query_create_sensordata_hypertable = "SELECT create_hypertable('sensor_data', 'time');"

    cursor.execute(query_create_sensordata_table)
    # cursor.execute(query_create_sensordata_hypertable)
    conn.commit()

    SQL = "INSERT INTO sensors (type, location) VALUES (%s, %s);"
    sensors = [('a', 'floor'), ('a', 'ceiling'), ('b', 'floor'), ('b', 'ceiling')]
    for sensor in sensors:
        try:
            data = (sensor[0], sensor[1])
            cursor.execute(SQL, data)
        except (Exception, psycopg2.Error) as error:
            print(error.pgerror)
    conn.commit()

    fast_insert(conn)


    cursor.close()


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
