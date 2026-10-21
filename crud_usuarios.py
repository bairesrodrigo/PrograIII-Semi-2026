from conexion import Conexion

class CrudUsuarios:
    def __init__(self):
        self.db = Conexion()

    def crud_usuarios_usss005825(self, datos):
        try:
            conexion = self.db.obtener_conexion()
            if not conexion:
                return {"status": "error", "msg": "Error de conexión a la base de datos"}
            
            cursor = conexion.cursor()
            accion = datos.get('accion', 'insertar')
            
            if accion == 'insertar':
                cursor.execute(
                    "INSERT INTO usuarios_usss005825 (usuario, clave, nombre, direccion, telefono) VALUES (%s, %s, %s, %s, %s)",
                    (datos.get('usuario'), datos.get('clave'), datos.get('nombre'), datos.get('direccion'), datos.get('telefono'))
                )
                conexion.commit()
                cursor.close()
                conexion.close()
                return {"status": "ok", "msg": "Usuario registrado correctamente"}
                
            elif accion == 'actualizar':
                id_usuario = datos.get('idUsuario')
                cursor.execute(
                    "UPDATE usuarios_usss005825 SET usuario = %s, clave = %s, nombre = %s, direccion = %s, telefono = %s WHERE idUsuario = %s",
                    (datos.get('usuario'), datos.get('clave'), datos.get('nombre'), datos.get('direccion'), datos.get('telefono'), id_usuario)
                )
                conexion.commit()
                cursor.close()
                conexion.close()
                return {"status": "ok", "msg": "Usuario actualizado correctamente"}
                
            cursor.close()
            conexion.close()
            return {"status": "error", "msg": "Acción no reconocida"}
        except Exception as e:
            return {"status": "error", "msg": str(e)}

    def consultar(self, buscar=""):
        try:
            conexion = self.db.obtener_conexion()
            if not conexion: return []
            cursor = conexion.cursor(dictionary=True)
            if buscar:
                query = "SELECT * FROM usuarios_usss005825 WHERE nombre LIKE %s OR usuario LIKE %s"
                cursor.execute(query, (f'%{buscar}%', f'%{buscar}%'))
            else:
                cursor.execute("SELECT * FROM usuarios_usss005825")
            resultado = cursor.fetchall()
            cursor.close()
            conexion.close()
            return resultado
        except Exception as e:
            return []

    def eliminar(self, id_usuario):
        try:
            conexion = self.db.obtener_conexion()
            if not conexion: return {"status": "error", "msg": "Error de conexión"}
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM usuarios_usss005825 WHERE idUsuario = %s", (id_usuario,))
            conexion.commit()
            cursor.close()
            conexion.close()
            return {"status": "ok", "msg": "Usuario eliminado correctamente"}
        except Exception as e:
            return {"status": "error", "msg": str(e)}

    def validar_login(self, usuario, clave):
        try:
            conexion = self.db.obtener_conexion()
            if not conexion: return False
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios_usss005825 WHERE usuario = %s AND clave = %s", (usuario, clave))
            user = cursor.fetchone()
            cursor.close()
            conexion.close()
            return user is not None
        except Exception as e:
            return False