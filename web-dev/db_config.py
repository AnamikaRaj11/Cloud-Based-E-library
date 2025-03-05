import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rahul@103",
        database="CloudShelf"
    )
