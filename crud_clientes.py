import mysql.connector

class crud_clientes:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'db_sistema_impuestos'
        }

    def obtener_conexion(self):
        return mysql.connector.connect(**self.db_config)

    def consultar(self, buscar):
        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            if buscar:
                query = "SELECT * FROM clientes WHERE nombre LIKE %s OR codigo LIKE %s"
                cursor.execute(query, (f'%{buscar}%', f'%{buscar}%'))
            else:
                cursor.execute("SELECT * FROM clientes")
            resultado = cursor.fetchall()
            conn.close()
            return resultado
        except Exception as e:
            return []

    def administrar(self, datos):
        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            accion = datos.get('accion', 'insertar')
            
            if accion == 'insertar':
                cursor.execute(
                    "INSERT INTO clientes (codigo, nombre, direccion, telefono, tipo) VALUES (%s, %s, %s, %s, %s)",
                    (datos.get('codigo'), datos.get('nombre'), datos.get('direccion'), datos.get('telefono'), datos.get('tipo', 'EMPRESA'))
                )
                conn.commit()
                conn.close()
                return "Cliente registrado correctamente"
                
            elif accion == 'actualizar':
                cliente_id = datos.get('idCliente') or datos.get('id')
                cursor.execute(
                    "UPDATE clientes SET codigo = %s, nombre = %s, direccion = %s, telefono = %s, tipo = %s WHERE idCliente = %s",
                    (datos.get('codigo'), datos.get('nombre'), datos.get('direccion'), datos.get('telefono'), datos.get('tipo', 'EMPRESA'), cliente_id)
                )
                conn.commit()
                conn.close()
                return "Cliente actualizado correctamente"
                
            elif accion == 'eliminar':
                cliente_id = datos.get('idCliente') or datos.get('id')
                cursor.execute("DELETE FROM clientes WHERE idCliente = %s OR codigo = %s", (cliente_id, cliente_id))
                conn.commit()
                conn.close()
                return "Cliente eliminado correctamente"
                
            return "Acción no reconocida"
        except Exception as e:
            return f"Error: {str(e)}"
            
    # NUEVO MÉTODO PARA ELIMINAR
    def eliminar(self, cliente_id):
        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            # Busca por id, idCliente o codigo para asegurar que encuentre el registro
            cursor.execute("DELETE FROM clientes WHERE id = %s OR idCliente = %s OR codigo = %s", (cliente_id, cliente_id, cliente_id))
            conn.commit()
            conn.close()
            return "Cliente eliminado correctamente"
        except Exception as e:
            return f"Error al eliminar: {str(e)}"