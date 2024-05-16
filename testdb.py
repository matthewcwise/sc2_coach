import psycopg2
from psycopg2 import OperationalError

def create_connection():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="starcraft_replays",
            user="replay_user",
            password="62884399",
            host="localhost"
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        conn = None
    return conn

def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query executed successfully")
    except OperationalError as e:
        print(f"The error '{e}' occurred")

# Example connection test
connection = create_connection()
if connection is not None:
    # Test query
    execute_query(connection, "SELECT * FROM replays;")
    connection.close()
