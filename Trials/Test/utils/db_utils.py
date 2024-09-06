import psycopg2
from psycopg2 import OperationalError
import os

def create_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PWD"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()
        print("Connection to PostgreSQL DB successful")
        return conn, cursor
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None, None
