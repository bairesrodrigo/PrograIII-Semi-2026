import mysql.connector
import math
import datetime
import re

class CrudImpuestos:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'db_sistema_impuestos'
        }

    def obtener_conexion(self):
        return mysql.connector.connect(**self.db_config)

    def buscar_tarifa(self, balance, producto_id):
        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT * FROM tarifas WHERE producto_id = %s AND %s BETWEEN desde AND hasta",
                (producto_id, balance)
            )
            tarifa = cursor.fetchone()
            conn.close()
            
            if not tarifa:
                return None, "No existe una tarifa configurada para el balance indicado."
            return tarifa, "ok"
        except Exception as e:
            return None, str(e)

    def calcular_impuesto_mensual(self, balance, tarifa):
        precio_base = float(tarifa['precio_base'])
        adicional = float(tarifa.get('adicional', 0)) if 'adicional' in tarifa else 0.0
        
        if balance <= 500.00:
            return round(precio_base, 2)
        elif balance <= 1000.00:
            excedente = balance - 500.00
            bloques = math.ceil(excedente / 500.0)
            return round(precio_base + (bloques * adicional), 2)
        elif balance <= 6000.00:
            excedente = balance - float(tarifa['desde'])
            bloques = math.ceil(excedente / 1000.0) if adicional > 0 else 0
            return round(precio_base + (bloques * adicional), 2)
        else:
            return round(precio_base, 2)

    def registrar_periodo(self, datos):
        cliente_id = datos.get('cliente_id')
        producto_id = datos.get('producto_id', 11801)
        fecha_desde = str(datos.get('fecha_desde', ''))
        fecha_hasta = str(datos.get('fecha_hasta', ''))
        balance = float(datos.get('balance', 0))

        try:
            # Validación: Evita registrar períodos con años futuros (mayores al año actual 2026)
            anio_actual = datetime.date.today().year
            texto_a_validar = f"{fecha_desde} {fecha_hasta}"
            anios_encontrados = re.findall(r'\b(20\d{2})\b', texto_a_validar)
            
            if anios_encontrados:
                for anio_str in anios_encontrados:
                    if int(anio_str) > anio_actual:
                        return f"Error: No se pueden registrar períodos de años futuros ({anio_str})."

            conn = self.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            
            # Validación: Las personas naturales / particulares no pueden registrar periodos comerciales
            cursor.execute("SELECT tipo, nombre FROM clientes WHERE idCliente = %s", (cliente_id,))
            cliente = cursor.fetchone()
            
            if cliente and ('particular' in cliente.get('tipo', '').lower() or 'natural' in cliente.get('tipo', '').lower()):
                conn.close()
                return "Error: Las personas naturales no pueden registrar períodos comerciales."

            # Buscar la tarifa correspondiente
            cursor.execute(
                "SELECT * FROM tarifas WHERE producto_id = %s AND %s BETWEEN desde AND hasta",
                (producto_id, balance)
            )
            tarifa = cursor.fetchone()
            
            if not tarifa:
                conn.close()
                return "No existe una tarifa configurada para el balance indicado."

            precio_mensual = self.calcular_impuesto_mensual(balance, tarifa)
            tarifa_aplicada_id = tarifa.get('id', tarifa.get('idTarifa', 1))
            precio_base = tarifa['precio_base']
            
            # Validar superposición de períodos
            cursor.execute("""
                SELECT COUNT(*) as total FROM periodos_empresas 
                WHERE cliente_id = %s AND producto_id = %s 
                AND ((fecha_desde <= %s AND fecha_hasta >= %s) OR (fecha_desde <= %s AND fecha_hasta >= %s))
            """, (cliente_id, producto_id, fecha_hasta, fecha_hasta, fecha_desde, fecha_desde))
            
            resultado_overlap = cursor.fetchone()
            overlap = resultado_overlap['total'] if resultado_overlap else 0

            if overlap > 0:
                conn.close()
                return "El período indicado se superpone con un período existente."

            # Insertar el período
            cursor.execute("""
                INSERT INTO periodos_empresas 
                (cliente_id, producto_id, fecha_desde, fecha_hasta, balance, precio_base, precio_mensual, tarifa_aplicada_id, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'VIGENTE')
            """, (cliente_id, producto_id, fecha_desde, fecha_hasta, balance, precio_base, precio_mensual, tarifa_aplicada_id))
            
            conn.commit()
            conn.close()
            return "ok"
            
        except Exception as e:
            return f"Error en base de datos: {str(e)}"

    def listar_tarifas(self, producto_id=11801):
        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tarifas WHERE producto_id = %s ORDER BY desde ASC", (producto_id,))
            tarifas = cursor.fetchall()
            conn.close()
            return tarifas
        except Exception as e:
            print("Error al listar tarifas:", e)
            return []

    def listar_periodos(self, cliente_id):
        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM periodos_empresas WHERE cliente_id = %s", (cliente_id,))
            periodos = cursor.fetchall()
            
            for p in periodos:
                if p.get('fecha_desde'):
                    p['fecha_desde'] = str(p['fecha_desde'])
                if p.get('fecha_hasta'):
                    p['fecha_hasta'] = str(p['fecha_hasta'])
                if p.get('created_at'):
                    p['created_at'] = str(p['created_at'])
                if p.get('balance') is not None:
                    p['balance'] = float(p['balance'])
                if p.get('precio_base') is not None:
                    p['precio_base'] = float(p['precio_base'])
                if p.get('precio_mensual') is not None:
                    p['precio_mensual'] = float(p['precio_mensual'])
                    
            conn.close()
            return periodos
        except Exception as e:
            print("Error al listar períodos:", e)
            return []