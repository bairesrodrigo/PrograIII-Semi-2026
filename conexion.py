import mysql.connector
from mysql.connector import Error


class Conexion:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "db_sistema_impuestos"
        print("Conectando a la base de datos...")

        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.conexion.is_connected():
                print("Conexion exitosa")
            else:
                print("No se pudo conectar a la base de datos")
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def consultar(self, sql, valores=None):
        try:
            cursor = self.conexion.cursor(dictionary=True)
            if valores:
                cursor.execute(sql, valores)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
        except Error as e:
            print(f"Error al consultar la base de datos: {e}")
            return []

    def ejecutar(self, sql, valores=None):
        try:
            cursor = self.conexion.cursor()
            if valores:
                cursor.execute(sql, valores)
            else:
                cursor.execute(sql)
            self.conexion.commit()
            return "ok"
        except Error as e:
            print(f"Error al ejecutar en la base de datos: {e}")
            return str(e)