import mysql.connector
from mysql.connector import Error

class SingletonDB:
    _instance = None
    _connection = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonDB, cls).__new__(cls)
        return cls._instance

    def connect(self):
        if not self._connection or not self._connection.is_connected():
            try:
                self._connection = mysql.connector.connect(
                    host='localhost',
                    user='upds',
                    password='upds123',
                    database='upds_practicas'
                )
            except Error as e:
                print(f"Error al conectar a la base de datos: {e}")
                self._connection = None
        return self._connection

    def close(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

def get_db_connection():
    db = SingletonDB()
    return db.connect()
