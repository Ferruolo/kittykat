import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "andrewferruolo",
    "password": "password"
}

# If this was production, I would use serverside pooling with a queue/loadbalancer instead of this
# However, that's a bit overkill for this
# And I'd probably use an ORM
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    **DB_CONFIG
)

@contextmanager
def get_db_connection():
    connection = connection_pool.getconn()
    try:
        yield connection
    finally:
        connection_pool.putconn(connection)

def get_db_cursor():
    connection = connection_pool.getconn()
    try:
        cursor = connection.cursor()
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection_pool.putconn(connection)
