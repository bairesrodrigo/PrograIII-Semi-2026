import mysql.connector
from mysql.connector import Error

class Conexion:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "db_academica"

    def obtener_conexion(self):
        try:
            conexion = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return conexion
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None