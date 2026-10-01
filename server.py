from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib import parse 
from urllib.parse import urlparse, parse_qs
import crud_clientes
import crud_impuestos
import json

port = 3000
crudClientes = crud_clientes.crud_clientes()
crudImpuestos = crud_impuestos.CrudImpuestos()

class miServidor(SimpleHTTPRequestHandler):
    def do_POST(self):
        longitud = int(self.headers['Content-Length'])
        datos = self.rfile.read(longitud)
        datos = datos.decode("utf-8")
        datos = parse.unquote(datos)
        datos = json.loads(datos)
        
        if self.path == '/api/calcular-impuesto':
            balance = float(datos.get('balance', 0))
            producto_id = int(datos.get('producto_id', 11801))
            
            tarifa, mensaje = crudImpuestos.buscar_tarifa(balance, producto_id)
            if not tarifa:
                respuesta = {'status': 'error', 'msg': mensaje}
            else:
                precio_mensual = crudImpuestos.calcular_impuesto_mensual(balance, tarifa)
                respuesta = {
                    'status': 'ok',
                    'precio_mensual': precio_mensual,
                    'precio_base': str(tarifa['precio_base']),
                    'adicional': str(tarifa.get('adicional', 0)),
                    'porcentaje': str(tarifa.get('porcentaje', 0))
                }
                
        elif self.path == '/api/guardar-periodo':
            mensaje_res = crudImpuestos.registrar_periodo(datos)
            respuesta = {'msg': mensaje_res}
            
        else:
            respuesta = {'msg': crudClientes.administrar(datos)}

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(respuesta).encode("utf-8"))
        
    def do_GET(self):
        urlParse = urlparse(self.path)
        qs = parse_qs(urlParse.query)
       
        if urlParse.path == "/clientes":
            buscar = qs.get('buscar', [''])[0]
            datos = crudClientes.consultar(buscar)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(datos).encode("utf-8"))
            
        elif urlParse.path == "/api/periodos":
            cliente_id_str = qs.get('cliente_id', ['0'])[0]
            try:
                cliente_id = int(cliente_id_str)
            except ValueError:
                cliente_id = 0

            datos = crudImpuestos.listar_periodos(cliente_id)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(datos).encode("utf-8"))
        
        elif urlParse.path == "/" or self.path == "/":
            self.path = "/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def do_PUT(self):
        longitud = int(self.headers.get('Content-Length', 0))
        datos = self.rfile.read(longitud).decode("utf-8")
        try:
            datos = json.loads(datos) if datos else {}
        except:
            datos = {}

        urlParse = urlparse(self.path)
        if urlParse.path.startswith('/clientes/actualizar/'):
            try:
                cliente_id = urlParse.path.split('/')[-1]
                datos['idCliente'] = cliente_id
                datos['accion'] = 'actualizar'
                
                mensaje_res = crudClientes.administrar(datos)
                
                if "Error" in mensaje_res:
                    respuesta = {'status': 'error', 'msg': mensaje_res}
                else:
                    respuesta = {'status': 'ok', 'msg': mensaje_res}
            except Exception as e:
                respuesta = {'status': 'error', 'msg': str(e)}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        urlParse = urlparse(self.path)
        if urlParse.path.startswith('/clientes/eliminar/'):
            try:
                cliente_id = urlParse.path.split('/')[-1]
                
                # Llamamos directamente al método de eliminación que acabamos de crear en crud_clientes
                mensaje_res = crudClientes.eliminar(cliente_id)
                
                if "Error" in mensaje_res:
                    respuesta = {'status': 'error', 'msg': mensaje_res}
                else:
                    respuesta = {'status': 'ok', 'msg': mensaje_res}
            except Exception as e:
                respuesta = {'status': 'error', 'msg': str(e)}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

print(f"Servidor corriendo en el puerto {port}")
server = HTTPServer(("localhost", port), miServidor)
server.serve_forever()