import mysql.connector
import os

def connectionBD():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "db"),
            user=os.environ.get("MYSQL_USER", "root"),
            passwd=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DB", "crud_python"),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            raise_on_warnings=True
        )
        if connection.is_connected():
            return connection

    except mysql.connector.Error as error:
        print(f"No se pudo conectar: {error}")
