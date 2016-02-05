import cassandra.concurrent

def store_readings_concurrently(session, rows):
    """ Stores given rows using concurrency """

    add_reading_query = session.prepare("""
        INSERT INTO readings_by_sensor (sensor, parameter, time, value)
        VALUES (?, ?, ?, ?)
        """)
    for param, readings in rows.items():
        parameters = []
        for i, row in enumerate(readings):
            print(row[0], row[1], (row[2]), float(row[3]))
            parameters.append((row[0], row[1], (row[2]), (row[3]),))

            cassandra.concurrent.execute_concurrent_with_args(session, add_reading_query, parameters, concurrency=50)